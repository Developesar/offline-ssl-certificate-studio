"""mohamadmilad hadad - offline certificate studio."""
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from converter import FORMATS, ConversionError, read_material, assemble, plan_outputs, write_outputs

BG = '#101725'
CARD = '#192335'
TEXT = '#e7edf7'
MUTED = '#a6b5cd'
ACCENT = '#51dfc0'


def resource(name):
    return Path(getattr(sys, '_MEIPASS', Path(__file__).parent)) / name


class Studio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('mohamadmilad hadad | SSL Certificate Studio')
        self.geometry('1100x830')
        self.minsize(960, 700)
        self.configure(bg=BG)
        try:
            self.iconbitmap(str(resource('assets/app.ico')))
        except tk.TclError:
            pass
        self.cert_path = tk.StringVar()
        self.key_path = tk.StringVar()
        self.input_password = tk.StringVar()
        self.output_password = tk.StringVar()
        self.confirm_password = tk.StringVar()
        self.output_folder = tk.StringVar(value=str(Path.home() / 'Desktop'))
        self.stem = tk.StringVar(value='certificate')
        self.encrypt_key = tk.BooleanVar(value=True)
        self.legacy = tk.BooleanVar()
        self.show_passwords = tk.BooleanVar()
        self.chains = []
        self.flags = {f: tk.BooleanVar(value=f == 'pem') for f in FORMATS}
        self.password_entries = []
        self.loaded_path = None
        self.setup_style()
        self.build()
        self.protocol('WM_DELETE_WINDOW', self.close)

    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('.', background=CARD, foreground=TEXT, font=('Segoe UI', 10))
        style.configure('TFrame', background=CARD)
        style.configure('TLabel', background=CARD, foreground=TEXT)
        style.configure('Muted.TLabel', foreground=MUTED, font=('Segoe UI', 9))
        style.configure('Title.TLabel', font=('Segoe UI Semibold', 13))
        style.configure('TEntry', fieldbackground='#0e1624', foreground=TEXT, bordercolor='#33445f', padding=7)
        style.configure('TCombobox', fieldbackground='#0e1624', foreground=TEXT, padding=5)
        style.map('TCombobox', fieldbackground=[('readonly', '#0e1624')], foreground=[('readonly', TEXT)])
        style.configure('TButton', background='#2c3c55', foreground=TEXT, borderwidth=0, padding=(13, 7))
        style.map('TButton', background=[('active', '#405878')])
        style.configure('Accent.TButton', background=ACCENT, foreground='#09261f', font=('Segoe UI Semibold', 11))
        style.map('Accent.TButton', background=[('active', '#91f1da')])
        style.configure('TCheckbutton', background=CARD, foreground=TEXT)
        style.map('TCheckbutton', background=[('active', CARD)])
        self.option_add('*TCombobox*Listbox.background', CARD)
        self.option_add('*TCombobox*Listbox.foreground', TEXT)

    def build(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill='x', padx=25, pady=(19, 14))
        mark = tk.Canvas(header, width=48, height=52, bg=BG, highlightthickness=0)
        mark.pack(side='left', padx=(0, 12))
        mark.create_polygon(24, 3, 44, 11, 41, 33, 24, 48, 7, 33, 4, 11, fill='#1d7666', outline=ACCENT, width=2)
        mark.create_line(14, 25, 21, 32, 34, 18, fill=ACCENT, width=4)
        title = tk.Frame(header, bg=BG)
        title.pack(side='left')
        tk.Label(title, text='mohamadmilad hadad', font=('Segoe UI Semibold', 23), fg=TEXT, bg=BG).pack(anchor='w')
        tk.Label(title, text='SSL CERTIFICATE STUDIO  /  LOCAL CONVERSION', font=('Segoe UI', 9), fg=MUTED, bg=BG).pack(anchor='w')
        tk.Label(header, text='●  OFFLINE', bg='#153e35', fg=ACCENT, padx=15, pady=8, font=('Segoe UI Semibold', 10)).pack(side='right')
        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill='x', padx=25, pady=(0, 10))
        tk.Label(toolbar, text='Your certificates. Your computer. No uploads.', bg=BG, fg=MUTED, font=('Segoe UI', 10)).pack(side='left')
        ttk.Button(toolbar, text='Format guide / راهنما', command=self.guide).pack(side='right')
        # Scrollable content accommodates small monitors and Windows display scaling.
        area = tk.Frame(self, bg=BG)
        area.pack(fill='both', expand=True, padx=25)
        self.canvas = tk.Canvas(area, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(area, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        body = tk.Frame(self.canvas, bg=BG)
        window = self.canvas.create_window((0, 0), window=body, anchor='nw')
        body.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfigure(window, width=e.width))
        self.bind_all('<MouseWheel>', lambda e: self.canvas.yview_scroll(int(-e.delta / 120), 'units'))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        inputs = self.card(body, '01  /  SOURCE FILES', 0, 0)
        inputs.columnconfigure(1, weight=1)
        self.path_row(inputs, 1, 'Certificate', self.cert_path, self.choose_cert)
        self.path_row(inputs, 2, 'Private key', self.key_path, self.choose_key)
        ttk.Label(inputs, text='Private key is required for PFX / P12 and key exports.', style='Muted.TLabel').grid(row=3, column=0, columnspan=3, sticky='w', pady=(3, 8))
        ttk.Label(inputs, text='Input password').grid(row=4, column=0, sticky='w', padx=(0, 8))
        self.password_entry(inputs, self.input_password).grid(row=4, column=1, columnspan=2, sticky='ew')
        ttk.Label(inputs, text='For an encrypted source key or PFX / P12.', style='Muted.TLabel').grid(row=5, column=0, columnspan=3, sticky='w', pady=(3, 9))
        ttk.Label(inputs, text='CA chain').grid(row=6, column=0, sticky='w')
        self.chain_label = ttk.Label(inputs, text='No extra CA files', style='Muted.TLabel')
        self.chain_label.grid(row=6, column=1, sticky='w')
        actions = ttk.Frame(inputs)
        actions.grid(row=6, column=2)
        ttk.Button(actions, text='Add', command=self.add_chain).pack(side='left')
        ttk.Button(actions, text='Clear', command=self.clear_chain).pack(side='left', padx=(4, 0))
        ttk.Button(inputs, text='Inspect certificate', command=self.inspect).grid(row=7, column=0, columnspan=3, sticky='ew', pady=(14, 8))
        self.cert_choice = ttk.Combobox(inputs, state='readonly')
        self.cert_choice.grid(row=8, column=0, columnspan=3, sticky='ew')
        self.cert_choice.bind('<<ComboboxSelected>>', lambda e: self.inspect(keep_selection=True))
        self.info = tk.Text(inputs, height=7, bg='#0e1624', fg=MUTED, font=('Segoe UI', 9), relief='flat', wrap='word', padx=10, pady=8, state='disabled')
        self.info.grid(row=9, column=0, columnspan=3, sticky='ew', pady=(8, 0))
        self.set_info('Load a certificate to see its identity, expiry and SHA-256 fingerprint.\n\nPEM, CRT, CER, DER, P7B, P7C, PFX and P12 are detected by content.')
        formats = self.card(body, '02  /  OUTPUT FORMATS', 0, 1)
        for row, (f, (label, _, needs_key)) in enumerate(FORMATS.items(), 1):
            ttk.Checkbutton(formats, text=label + ('  • key' if needs_key else ''), variable=self.flags[f]).grid(row=row, column=0, sticky='w', pady=2)
        buttons = ttk.Frame(formats)
        buttons.grid(row=len(FORMATS) + 1, column=0, sticky='ew', pady=(9, 0))
        ttk.Button(buttons, text='Certificates', command=self.cert_only).pack(side='left')
        ttk.Button(buttons, text='Clear', command=lambda: [v.set(False) for v in self.flags.values()]).pack(side='left', padx=5)
        destination = self.card(body, '03  /  SAVE & PROTECT', 1, 0, 2)
        destination.columnconfigure(1, weight=1)
        destination.columnconfigure(3, weight=1)
        self.path_row(destination, 1, 'Output folder', self.output_folder, self.choose_folder, colspan=3)
        ttk.Label(destination, text='Filename base').grid(row=2, column=0, sticky='w', pady=6)
        ttk.Entry(destination, textvariable=self.stem).grid(row=2, column=1, columnspan=3, sticky='ew', pady=6)
        ttk.Label(destination, text='Output password').grid(row=3, column=0, sticky='w', padx=(0, 8))
        self.password_entry(destination, self.output_password).grid(row=3, column=1, sticky='ew')
        ttk.Label(destination, text='Confirm password').grid(row=3, column=2, padx=12)
        self.password_entry(destination, self.confirm_password).grid(row=3, column=3, columnspan=2, sticky='ew')
        opts = ttk.Frame(destination)
        opts.grid(row=4, column=0, columnspan=5, sticky='ew', pady=(10, 3))
        ttk.Checkbutton(opts, text='Encrypt exported private keys', variable=self.encrypt_key).pack(side='left')
        ttk.Checkbutton(opts, text='Legacy PFX (older systems)', variable=self.legacy).pack(side='left', padx=18)
        ttk.Checkbutton(opts, text='Show passwords', variable=self.show_passwords, command=self.toggle_passwords).pack(side='right')
        ttk.Label(destination, text='PFX / P12 always use an output password. Modern encryption is the default.', style='Muted.TLabel').grid(row=5, column=0, columnspan=5, sticky='w', pady=(4, 0))
        footer = tk.Frame(self, bg=BG)
        footer.pack(fill='x', padx=25, pady=15)
        self.status = tk.StringVar(value='Ready  •  Files and passwords stay on this computer')
        tk.Label(footer, textvariable=self.status, bg=BG, fg=ACCENT, font=('Segoe UI', 10)).pack(side='left')
        ttk.Button(footer, text='Convert & save  →', style='Accent.TButton', command=self.convert).pack(side='right')
        ttk.Button(footer, text='Clear passwords', command=self.clear_passwords).pack(side='right', padx=8)

    def card(self, parent, title, row, column, span=1):
        frame = ttk.Frame(parent, padding=17)
        frame.grid(row=row, column=column, columnspan=span, sticky='nsew', padx=(0, 10 if column == 0 and span == 1 else 0), pady=(0, 12))
        ttk.Label(frame, text=title, style='Title.TLabel').grid(row=0, column=0, columnspan=5, sticky='w', pady=(0, 13))
        return frame

    def path_row(self, frame, row, label, var, command, colspan=1):
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky='w', padx=(0, 8), pady=5)
        ttk.Entry(frame, textvariable=var).grid(row=row, column=1, columnspan=colspan, sticky='ew', pady=5)
        ttk.Button(frame, text='Browse', command=command).grid(row=row, column=1 + colspan, padx=(7, 0), pady=5)

    def password_entry(self, frame, var):
        entry = ttk.Entry(frame, textvariable=var, show='●')
        self.password_entries.append(entry)
        return entry

    def choose_cert(self):
        path = filedialog.askopenfilename(title='Select certificate or certificate bundle', filetypes=[('Certificates', '*.pem *.cer *.crt *.der *.pfx *.p12 *.p7b *.p7c *.ca-bundle *.bundle'), ('All files', '*.*')])
        if path:
            self.cert_path.set(path)
            self.loaded_path = None
            self.cert_choice.set('')
            self.stem.set(Path(path).stem)
            self.inspect()

    def choose_key(self):
        path = filedialog.askopenfilename(title='Select the original private key', filetypes=[('Private keys', '*.key *.pem *.der *.pk8'), ('All files', '*.*')])
        if path:
            self.key_path.set(path)

    def add_chain(self):
        paths = filedialog.askopenfilenames(title='Select issuer / intermediate / root certificates', filetypes=[('Certificates', '*.pem *.cer *.crt *.der *.p7b *.p7c *.ca-bundle *.bundle'), ('All files', '*.*')])
        self.chains = list(dict.fromkeys(self.chains + list(paths)))
        self.chain_label.configure(text=f'{len(self.chains)} CA file(s)' if self.chains else 'No extra CA files')

    def clear_chain(self):
        self.chains.clear()
        self.chain_label.configure(text='No extra CA files')

    def choose_folder(self):
        path = filedialog.askdirectory(title='Choose output folder')
        if path:
            self.output_folder.set(path)

    def set_info(self, text):
        self.info.configure(state='normal')
        self.info.delete('1.0', 'end')
        self.info.insert('1.0', text)
        self.info.configure(state='disabled')

    def inspect(self, keep_selection=False):
        if not self.cert_path.get():
            messagebox.showinfo('Select input', 'Choose a certificate file first.', parent=self)
            return
        try:
            material = read_material(self.cert_path.get(), self.input_password.get())
            idx = max(0, self.cert_choice.current()) if keep_selection else 0
            self.cert_choice['values'] = [f'{i + 1}. {c.subject.rfc4514_string()}' for i, c in enumerate(material.certificates)]
            self.cert_choice.current(min(idx, len(material.certificates) - 1))
            self.loaded_path = self.cert_path.get()
            cert = material.certificates[self.cert_choice.current()]
            try:
                names = ', '.join(cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName))
            except x509.ExtensionNotFound:
                names = '—'
            fp = cert.fingerprint(hashes.SHA256()).hex(':').upper()
            self.set_info(f'Subject: {cert.subject.rfc4514_string()}\nIssuer: {cert.issuer.rfc4514_string()}\nDNS: {names}\nValid: {cert.not_valid_before_utc:%Y-%m-%d} → {cert.not_valid_after_utc:%Y-%m-%d} (UTC)\nSHA-256: {fp}\nCertificates: {len(material.certificates)} | Embedded key: {"yes" if material.key else "no"}')
            self.status.set('Certificate inspected  •  Select your outputs')
        except Exception as exc:
            self.loaded_path = None
            self.cert_choice.set('')
            self.set_info('Unable to inspect this input. Enter its password if it is encrypted, then click Inspect certificate.')
            self.error(exc)

    def error(self, exc):
        self.status.set('Check input  •  Conversion was not completed')
        text = str(exc) if isinstance(exc, (ConversionError, OSError)) else 'The file could not be processed. Check its format and password.'
        messagebox.showerror('Conversion error', text, parent=self)

    def cert_only(self):
        for f, var in self.flags.items():
            var.set(f in ('pem', 'crt', 'cer_der', 'der', 'fullchain', 'p7b'))

    def toggle_passwords(self):
        for entry in self.password_entries:
            entry.configure(show='' if self.show_passwords.get() else '●')

    def clear_passwords(self):
        for var in (self.input_password, self.output_password, self.confirm_password):
            var.set('')
        self.show_passwords.set(False)
        self.toggle_passwords()

    def convert(self):
        try:
            if not self.cert_path.get():
                raise ConversionError('Select a certificate file first.')
            formats = [f for f, var in self.flags.items() if var.get()]
            if self.output_password.get() != self.confirm_password.get():
                raise ConversionError('Output passwords do not match.')
            idx = max(0, self.cert_choice.current()) if self.loaded_path == self.cert_path.get() else 0
            material = assemble(self.cert_path.get(), self.key_path.get(), self.chains, self.input_password.get(), idx)
            outputs = plan_outputs(material, formats, self.stem.get(), self.output_password.get(), self.encrypt_key.get(), self.legacy.get())
            folder = Path(self.output_folder.get())
            if not folder.is_dir():
                raise ConversionError('Choose an existing output folder.')
            targets = [(folder / name).resolve() for name in outputs]
            inputs = [Path(p).resolve() for p in [self.cert_path.get(), self.key_path.get(), *self.chains] if p]
            if any(target in inputs for target in targets):
                raise ConversionError('An output would replace an input file. Choose a different filename or folder.')
            if not self.encrypt_key.get() and any(f in formats for f in ('key', 'pk8', 'combined')):
                if not messagebox.askyesno('Unencrypted private key', 'The selected key output will have no password protection. Anyone with the file can read the key. Save it unencrypted?', parent=self):
                    return
            existing = [p.name for p in targets if p.exists()]
            overwrite = False
            if existing:
                overwrite = messagebox.askyesno('Replace existing files?', 'Replace these files?\n\n' + '\n'.join(existing), parent=self)
                if not overwrite:
                    return
            paths = write_outputs(folder, outputs, overwrite)
            self.clear_passwords()
            self.status.set(f'Saved {len(paths)} file(s)  •  Password fields cleared')
            messagebox.showinfo('Conversion complete', f'Saved {len(paths)} file(s) locally:\n\n' + '\n'.join(str(p) for p in paths), parent=self)
        except Exception as exc:
            self.error(exc)

    def guide(self):
        dialog = tk.Toplevel(self)
        dialog.title('Format guide / راهنمای فرمت‌ها')
        dialog.geometry('790x600')
        dialog.configure(bg=BG)
        text = tk.Text(dialog, bg=CARD, fg=TEXT, font=('Segoe UI', 11), wrap='word', padx=22, pady=22, relief='flat')
        text.pack(fill='both', expand=True, padx=12, pady=12)
        text.insert('1.0', GUIDE)
        text.configure(state='disabled')

    def close(self):
        self.clear_passwords()
        self.destroy()


GUIDE = '''OFFLINE CERTIFICATE CONVERSION

1. Choose the certificate delivered by your certificate authority.
2. For PFX / P12, add the ORIGINAL private key from the CSR process.
3. Add the intermediate / root CA files if you need a complete chain.
4. Select outputs, choose a folder, and set an output password when needed.
5. Click Convert & save. Password fields clear after a successful conversion.

.pem — Base64 text with BEGIN / END blocks; certificates or keys.
.crt / .cer — X.509 certificates; either PEM text or DER binary.
.der — Binary certificate encoding.
.pfx / .p12 — PKCS#12: certificate, matching private key, optional CA chain.
.p7b / .p7c — PKCS#7 certificate bundle; contains no private key.
.key / .pk8 / .p8 — Private keys; usually PKCS#8 or older key encodings.
.ca-bundle / .bundle / fullchain.pem — Conventional names for PEM chains.
.csr / .p10 / .req — Signing request, made before the CA issues a certificate.
.crl — CA revocation list, published and signed by the CA.
.jks / .keystore / .jceks — Java keystores; require separate Java tooling.
.p7m / .p7s — CMS messages / signatures; not plain certificate conversions.
.spc — Legacy certificate-container naming, often PKCS#7.

This app exports the 16 formats shown in the main window. CSR, CRL,
Java keystores, signatures and token objects are listed for reference;
they are not created by changing a certificate's extension.

PEM / CRT / CER / DER export the selected certificate only.
Full chain and P7B / P7C include all supplied certificates.
CA bundle excludes the selected certificate. Issuer links and signatures
are checked when ordering a supplied chain. This does not validate trust,
hostname, revocation or completeness against a system trust store.
For bundles with several certificates, choose a certificate in the dropdown.
A supplied private key automatically selects its matching certificate.

All processing is local. No network, uploads, telemetry or password files.
Keep input and output files in a local folder if you do not want a cloud-sync
service on your computer to upload them. Protect the computer and backups.
Passwords live briefly in process memory; Python cannot guarantee memory erasure.
Private-key files are encrypted by default. PFX encryption is not a substitute
for controlling access to the file. Legacy PFX uses older 3DES / SHA-1 options.

فارسی:
برای تبدیل CER یا PEM به PFX باید کلید خصوصی اصلی را داشته باشید.
گواهی صادرشده شامل کلید خصوصی نیست و برنامه نمی‌تواند آن را بازسازی کند.
فایل واسط صادرکننده را از بخش CA chain اضافه کنید.
برای جلوگیری از همگام‌سازی خودکار، پوشه خروجی را روی فضای محلی انتخاب کنید.
همه تبدیل‌ها آفلاین هستند؛ برنامه اطلاعاتی به هیچ سایتی ارسال نمی‌کند.
'''


if __name__ == '__main__':
    Studio().mainloop()
