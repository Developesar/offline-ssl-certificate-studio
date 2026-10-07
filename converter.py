"""Offline X.509 conversion; no external commands or network access."""
from dataclasses import dataclass
from pathlib import Path
import os
import re
import tempfile

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization as ser
from cryptography.hazmat.primitives.serialization import pkcs12, pkcs7


class ConversionError(ValueError):
    pass


@dataclass
class Material:
    certificates: list
    key: object = None


# id: (label, extension, needs private key)
FORMATS = {
    'pem': ('PEM certificate', '.pem', False),
    'crt': ('CRT certificate (PEM)', '.crt', False),
    'cer_pem': ('CER certificate (PEM)', '.cer', False),
    'cer_der': ('CER certificate (DER)', '.der.cer', False),
    'der': ('DER certificate', '.der', False),
    'fullchain': ('Full chain (PEM)', '.fullchain.pem', False),
    'chain': ('CA chain / bundle (PEM)', '.ca-bundle', False),
    'p7b': ('PKCS#7 / P7B (DER)', '.p7b', False),
    'p7c': ('PKCS#7 / P7C (DER)', '.p7c', False),
    'p7b_pem': ('PKCS#7 / P7B (PEM)', '.pem.p7b', False),
    'pfx': ('PKCS#12 / PFX', '.pfx', True),
    'p12': ('PKCS#12 / P12', '.p12', True),
    'key': ('Private key (PKCS#8 PEM)', '.key', True),
    'pk8': ('Private key (PKCS#8 DER)', '.pk8', True),
    'combined': ('Certificate + chain + key (PEM)', '.combined.pem', True),
    'pub': ('Public key (PEM)', '.public.pem', False),
}


def password_bytes(password):
    return password.encode('utf-8') if password else None


def read_material(path, password=''):
    """Sniff PEM, DER X.509, PKCS#7, PKCS#12; keep embedded private key."""
    data = Path(path).read_bytes()
    if not data or len(data) > 32 * 1024 * 1024:
        raise ConversionError('The input is empty or exceeds 32 MB.')
    certs = []
    key = None
    if b'-----BEGIN' in data:
        blocks = re.findall(rb'-----BEGIN ([A-Z0-9 ]+)-----.*?-----END \1-----', data, re.S)
        cert_blocks = re.findall(rb'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----', data, re.S)
        try:
            certs = [x509.load_pem_x509_certificate(block) for block in cert_blocks]
            if b'PKCS7' in blocks:
                certs.extend(pkcs7.load_pem_pkcs7_certificates(data))
            key_blocks = re.findall(rb'-----BEGIN (?:ENCRYPTED |RSA |EC |DSA )?PRIVATE KEY-----.*?-----END (?:ENCRYPTED |RSA |EC |DSA )?PRIVATE KEY-----', data, re.S)
            if len(key_blocks) > 1:
                raise ConversionError('Multiple private keys found. Select a file containing only one key.')
            if key_blocks:
                key = load_private_key_data(key_blocks[0], password)
        except ConversionError:
            raise
        except ValueError as exc:
            raise ConversionError('Invalid PEM certificate or PKCS#7 bundle.') from exc
        if not certs:
            raise ConversionError('No certificate found. Use the private-key field for key-only files.')
    else:
        try:
            certs = [x509.load_der_x509_certificate(data)]
        except ValueError:
            try:
                certs = pkcs7.load_der_pkcs7_certificates(data)
            except ValueError:
                try:
                    key, cert, additional = pkcs12.load_key_and_certificates(data, password_bytes(password))
                    certs = ([cert] if cert else []) + list(additional or [])
                except ValueError as exc:
                    raise ConversionError('Unrecognized certificate, damaged file, or incorrect PFX/P12 password.') from exc
    if not certs:
        raise ConversionError('The file contains no certificates.')
    return Material(unique(certs), key)


def load_private_key_data(data, password=''):
    loader = ser.load_pem_private_key if b'-----BEGIN' in data else ser.load_der_private_key
    try:
        return loader(data, password=password_bytes(password))
    except TypeError:
        # A supplied password is harmless for an unencrypted key.
        if password:
            try:
                return loader(data, password=None)
            except (ValueError, TypeError):
                pass
    except ValueError:
        pass
    raise ConversionError('Cannot open the private key. Check the key file and its input password.')


def unique(certs):
    seen, result = set(), []
    for cert in certs:
        fp = cert.fingerprint(hashes.SHA256())
        if fp not in seen:
            seen.add(fp)
            result.append(cert)
    return result


def public_bytes(key):
    return key.public_bytes(ser.Encoding.DER, ser.PublicFormat.SubjectPublicKeyInfo)


def assemble(certificate_path, key_path='', chain_paths=(), password='', selected_index=0):
    material = read_material(certificate_path, password)
    if key_path:
        key_data = Path(key_path).read_bytes()
        if not key_data or len(key_data) > 1024 * 1024:
            raise ConversionError('The private key input is empty or exceeds 1 MB.')
        material.key = load_private_key_data(key_data, password)
    if not 0 <= selected_index < len(material.certificates):
        raise ConversionError('Choose a certificate again after changing the input file.')
    leaf = material.certificates[selected_index]
    if material.key is not None:
        matches = [c for c in material.certificates if public_bytes(c.public_key()) == public_bytes(material.key.public_key())]
        if not matches:
            raise ConversionError('The private key does not match any certificate in the input file.')
        leaf = matches[0]
    all_certs = list(material.certificates)
    for path in chain_paths:
        all_certs.extend(read_material(path, password).certificates)
    all_certs = unique(all_certs)
    remaining = [c for c in all_certs if c != leaf]
    ordered = [leaf]
    current = leaf
    while remaining:
        if current.issuer == current.subject:
            raise ConversionError('The bundle contains certificates unrelated to the selected certificate.')
        candidates = [c for c in remaining if c.subject == current.issuer]
        verified = []
        for issuer in candidates:
            try:
                current.verify_directly_issued_by(issuer)
                verified.append(issuer)
            except (ValueError, TypeError, x509.InvalidVersion):
                pass
            except Exception as exc:
                # Signature failure / unsupported signature: never silently add a bad issuer.
                from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
                if not isinstance(exc, (InvalidSignature, UnsupportedAlgorithm)):
                    raise
        if len(verified) != 1:
            raise ConversionError('The CA chain is incomplete, unrelated, or ambiguous. Supply one valid issuer path.')
        current = verified[0]
        ordered.append(current)
        remaining.remove(current)
    return Material(ordered, material.key)


def encode(material, format_id, output_password='', encrypt_key=True, legacy=False):
    if format_id not in FORMATS:
        raise ConversionError('Unsupported output format.')
    certs, key = material.certificates, material.key
    leaf = certs[0]
    if FORMATS[format_id][2] and key is None:
        raise ConversionError('This output needs the original matching private key. A certificate cannot recreate it.')
    if format_id in ('pem', 'crt', 'cer_pem'):
        return leaf.public_bytes(ser.Encoding.PEM)
    if format_id in ('cer_der', 'der'):
        return leaf.public_bytes(ser.Encoding.DER)
    if format_id == 'fullchain':
        return b''.join(c.public_bytes(ser.Encoding.PEM) for c in certs)
    if format_id == 'chain':
        if len(certs) < 2:
            raise ConversionError('CA bundle output needs at least one issuer certificate. Add your CA chain.')
        return b''.join(c.public_bytes(ser.Encoding.PEM) for c in certs[1:])
    if format_id in ('p7b', 'p7c', 'p7b_pem'):
        return pkcs7.serialize_certificates(certs, ser.Encoding.PEM if format_id == 'p7b_pem' else ser.Encoding.DER)
    if format_id == 'pub':
        return leaf.public_key().public_bytes(ser.Encoding.PEM, ser.PublicFormat.SubjectPublicKeyInfo)
    if format_id in ('pfx', 'p12'):
        if not output_password:
            raise ConversionError('Set an output password for PFX / P12.')
        encryption = ser.BestAvailableEncryption(password_bytes(output_password))
        if legacy:
            encryption = (ser.PrivateFormat.PKCS12.encryption_builder()
                          .kdf_rounds(50000).key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC)
                          .hmac_hash(hashes.SHA1()).build(password_bytes(output_password)))
        try:
            return pkcs12.serialize_key_and_certificates(b'mohamadmilad hadad', key, leaf, certs[1:] or None, encryption)
        except (ValueError, TypeError) as exc:
            raise ConversionError('This key type is not supported by PKCS#12.') from exc
    if encrypt_key and not output_password:
        raise ConversionError('Set an output password for encrypted private-key files.')
    encryption = ser.BestAvailableEncryption(password_bytes(output_password)) if encrypt_key else ser.NoEncryption()
    encoding = ser.Encoding.DER if format_id == 'pk8' else ser.Encoding.PEM
    key_data = key.private_bytes(encoding, ser.PrivateFormat.PKCS8, encryption)
    if format_id == 'combined':
        return b''.join(c.public_bytes(ser.Encoding.PEM) for c in certs) + key_data
    return key_data


def plan_outputs(material, formats, stem, password='', encrypt_key=True, legacy=False):
    if not formats:
        raise ConversionError('Select at least one output format.')
    stem = stem.strip()
    if (not stem or stem in ('.', '..') or re.search(r'[<>:"/\\|?*\x00-\x1f]', stem)
            or stem.endswith(('.', ' ')) or stem.split('.')[0].upper() in
            {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}):
        raise ConversionError('Choose a valid Windows filename without a folder or extension.')
    return {stem + FORMATS[f][1]: encode(material, f, password, encrypt_key, legacy) for f in dict.fromkeys(formats)}


def write_outputs(directory, outputs, overwrite=False):
    """Stage complete outputs first; each file is committed atomically."""
    folder = Path(directory)
    if not folder.is_dir():
        raise ConversionError('Choose an existing output folder.')
    targets = [folder / name for name in outputs]
    if any(p.name != name or name in ('.', '..') or Path(name).is_absolute()
           for p, name in zip(targets, outputs)):
        raise ConversionError('Invalid output filename.')
    if not overwrite and any(p.exists() for p in targets):
        raise ConversionError('An output file already exists. Choose another name or approve replacement.')
    staged = []
    try:
        for target, data in zip(targets, outputs.values()):
            fd, name = tempfile.mkstemp(prefix='.ssl-', dir=folder)
            staged.append((Path(name), target))
            with os.fdopen(fd, 'wb') as handle:
                handle.write(data)
        for source, target in staged:
            if overwrite:
                os.replace(source, target)
            else:
                # Windows rename does not overwrite a destination created concurrently.
                os.rename(source, target)
    finally:
        for source, _ in staged:
            source.unlink(missing_ok=True)
    return targets
