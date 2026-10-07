import datetime as dt
from pathlib import Path
import tempfile
import unittest

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization as ser
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.serialization import pkcs12, pkcs7
from cryptography.x509.oid import NameOID
from converter import FORMATS, ConversionError, assemble, encode, read_material, load_private_key_data, plan_outputs, write_outputs


def issue(name, key, issuer=None, issuer_key=None, ca=False):
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name)])
    now = dt.datetime.now(dt.timezone.utc)
    return (x509.CertificateBuilder().subject_name(subject)
            .issuer_name(issuer.subject if issuer else subject)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - dt.timedelta(days=1)).not_valid_after(now + dt.timedelta(days=90))
            .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
            .sign(issuer_key or key, hashes.SHA256()))


class ConverterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.inter_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.root = issue('Test Root', cls.root_key, ca=True)
        cls.inter = issue('Test Intermediate', cls.inter_key, cls.root, cls.root_key, True)
        cls.leaf = issue('example.test', cls.key, cls.inter, cls.inter_key)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ssl-test-')
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name) / 'گواهی محلی'
        self.folder.mkdir()
        self.cert = self.folder / 'certificate.cer'
        self.cert.write_bytes(self.leaf.public_bytes(ser.Encoding.PEM))
        self.keyfile = self.folder / 'original.key'
        self.keyfile.write_bytes(self.key.private_bytes(ser.Encoding.PEM, ser.PrivateFormat.PKCS8, ser.BestAvailableEncryption(b'input secret')))
        self.ca = self.folder / 'chain.pem'
        self.ca.write_bytes(self.root.public_bytes(ser.Encoding.PEM) + self.inter.public_bytes(ser.Encoding.PEM))

    def material(self):
        return assemble(self.cert, self.keyfile, [self.ca], 'input secret')

    def test_all_exports_and_roundtrip(self):
        material = self.material()
        self.assertEqual(material.certificates, [self.leaf, self.inter, self.root])
        outputs = plan_outputs(material, list(FORMATS), 'تست', 'خروجی-secret')
        paths = write_outputs(self.folder, outputs)
        self.assertEqual(len(paths), 16)
        for f in ('pem', 'crt', 'cer_pem', 'cer_der', 'der', 'fullchain', 'p7b', 'p7c', 'p7b_pem', 'pfx', 'p12', 'combined'):
            path = self.folder / ('تست' + FORMATS[f][1])
            actual = read_material(path, 'خروجی-secret')
            self.assertIn(self.leaf, actual.certificates, f)
            if f in ('fullchain', 'p7b', 'p7c', 'p7b_pem', 'pfx', 'p12', 'combined'):
                self.assertEqual(len(actual.certificates), 3, f)
            if f in ('pfx', 'p12', 'combined'):
                self.assertIsNotNone(actual.key, f)
        for f in ('key', 'pk8'):
            data = outputs['تست' + FORMATS[f][1]]
            self.assertEqual(load_private_key_data(data, 'خروجی-secret').private_numbers(), self.key.private_numbers())
        self.assertEqual(read_material(self.folder / 'تست.ca-bundle').certificates, [self.inter, self.root])
        pub = ser.load_pem_public_key(outputs['تست.public.pem'])
        self.assertEqual(pub.public_numbers(), self.key.public_key().public_numbers())

    def test_der_detected_despite_pem_extension(self):
        path = self.folder / 'misnamed.pem'
        path.write_bytes(self.leaf.public_bytes(ser.Encoding.DER))
        self.assertEqual(read_material(path).certificates, [self.leaf])

    def test_matching_key_selects_leaf_in_unordered_bundle(self):
        self.cert.write_bytes(self.root.public_bytes(ser.Encoding.PEM) + self.leaf.public_bytes(ser.Encoding.PEM) + self.inter.public_bytes(ser.Encoding.PEM))
        self.assertEqual(assemble(self.cert, self.keyfile, [self.ca], 'input secret').certificates, [self.leaf, self.inter, self.root])

    def test_mismatched_key(self):
        self.keyfile.write_bytes(self.root_key.private_bytes(ser.Encoding.PEM, ser.PrivateFormat.PKCS8, ser.NoEncryption()))
        with self.assertRaisesRegex(ConversionError, 'does not match'):
            self.material()

    def test_missing_key_and_password(self):
        material = assemble(self.cert)
        self.assertTrue(encode(material, 'cer_der'))
        with self.assertRaisesRegex(ConversionError, 'original matching'):
            encode(material, 'pfx', 'secret')
        with self.assertRaisesRegex(ConversionError, 'output password'):
            encode(self.material(), 'pfx')
        with self.assertRaisesRegex(ConversionError, 'output password'):
            encode(self.material(), 'key')
        with self.assertRaisesRegex(ConversionError, 'CA bundle'):
            encode(material, 'chain')

    def test_wrong_password_and_embedded_key(self):
        with self.assertRaises(ConversionError):
            assemble(self.cert, self.keyfile, password='wrong')
        self.cert.write_bytes(self.cert.read_bytes() + self.keyfile.read_bytes())
        self.assertIsNotNone(assemble(self.cert, password='input secret').key)
        with self.assertRaises(ConversionError):
            read_material(self.cert, 'wrong')

    def test_bad_chain_and_invalid_signature(self):
        self.ca.write_bytes(self.root.public_bytes(ser.Encoding.PEM))
        with self.assertRaisesRegex(ConversionError, 'chain'):
            self.material()
        forged = issue('Test Intermediate', self.inter_key, self.root, self.root_key, True)
        other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        bad_leaf = issue('bad.test', self.key, forged, other)
        self.cert.write_bytes(bad_leaf.public_bytes(ser.Encoding.PEM))
        self.ca.write_bytes(forged.public_bytes(ser.Encoding.PEM))
        with self.assertRaisesRegex(ConversionError, 'chain'):
            self.material()

    def test_legacy_pfx_and_ec(self):
        payload = encode(self.material(), 'pfx', 'secret', legacy=True)
        key, cert, chain = pkcs12.load_key_and_certificates(payload, b'secret')
        self.assertEqual(cert, self.leaf)
        self.assertEqual(len(chain), 2)
        key = ec.generate_private_key(ec.SECP256R1())
        cert = issue('ec.test', key)
        self.cert.write_bytes(cert.public_bytes(ser.Encoding.PEM))
        self.keyfile.write_bytes(key.private_bytes(ser.Encoding.DER, ser.PrivateFormat.PKCS8, ser.NoEncryption()))
        mat = assemble(self.cert, self.keyfile)
        self.assertEqual(pkcs12.load_key_and_certificates(encode(mat, 'pfx', 'secret'), b'secret')[1], cert)

    def test_write_does_not_overwrite_without_consent(self):
        write_outputs(self.folder, {'existing.pem': b'original'})
        with self.assertRaises(ConversionError):
            write_outputs(self.folder, {'existing.pem': b'changed', 'new.pem': b'new'})
        self.assertEqual((self.folder / 'existing.pem').read_bytes(), b'original')
        self.assertFalse((self.folder / 'new.pem').exists())
        write_outputs(self.folder, {'existing.pem': b'changed'}, overwrite=True)
        self.assertEqual((self.folder / 'existing.pem').read_bytes(), b'changed')
        self.assertFalse(list(self.folder.glob('.ssl-*')))

    def test_invalid_names_and_corrupt_input(self):
        for name in ('../key', 'CON', 'x/y', 'a.', '', 'COM1.txt'):
            with self.assertRaises(ConversionError):
                plan_outputs(assemble(self.cert), ['pem'], name)
        self.cert.write_bytes(b'bad input')
        with self.assertRaises(ConversionError):
            read_material(self.cert)


if __name__ == '__main__':
    unittest.main()
