<p align="center"><img src="assets/banner.svg" alt="mohamadmilad hadad — Offline SSL Certificate Studio" width="100%"></p>

<p align="center">
  <a href="https://github.com/Developesar/offline-ssl-certificate-studio/releases/latest"><img alt="Version" src="https://img.shields.io/github/v/release/Developesar/offline-ssl-certificate-studio?color=51dfc0&style=for-the-badge"></a>
  <img alt="Platform" src="https://img.shields.io/badge/Windows-EXE-7dd3fc?style=for-the-badge">
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-51dfc0?style=for-the-badge"></a>
  <a href="https://github.com/Developesar/offline-ssl-certificate-studio/actions"><img alt="Tests" src="https://github.com/Developesar/offline-ssl-certificate-studio/actions/workflows/ci.yml/badge.svg"></a>
</p>

<p align="center"><b>Your certificates. Your computer. No uploads.</b><br>گواهی‌های شما، روی کامپیوتر شما، بدون آپلود.</p>

<p align="center"><a href="#فارسی">فارسی</a> · <a href="#english">English</a> · <a href="https://github.com/Developesar/offline-ssl-certificate-studio/releases/latest">Download EXE / دانلود</a> · <a href="CONTRIBUTING.md">Contribute / مشارکت</a></p>

## فارسی

**mohamadmilad hadad — SSL Certificate Studio** یک برنامه دسکتاپ با Python و Tkinter برای تبدیل محلی گواهی‌های SSL/TLS است. فایل‌های تحویلی صادرکننده، مثل PEM و CER، را بدهید و خروجی مناسب سرورتان را بسازید. نسخه اجرایی ویندوز نیازی به نصب Python یا OpenSSL ندارد.

### دریافت نسخه اول

از [صفحه انتشار v1.0.0](https://github.com/Developesar/offline-ssl-certificate-studio/releases/tag/v1.0.0)، فایل **mohamadmilad hadad.exe** را دانلود و اجرا کنید. هش SHA-256 در فایل `SHA256SUMS.txt` همان انتشار قرار دارد. برنامه نصب‌کننده و دسترسی Administrator نمی‌خواهد. فایل اجرایی نسخه اول امضای دیجیتال ناشر ندارد.

### امکانات

- ظاهر تیره با رنگ نعنایی، آیکون اختصاصی و فرم قابل پیمایش.
- تشخیص فرمت از محتوای فایل، حتی اگر پسوند نادرست باشد.
- دریافت گواهی، کلید خصوصی رمزدار یا بدون رمز، و چند فایل زنجیره CA.
- ساخت چند خروجی در یک نوبت؛ ۱۶ گزینه خروجی.
- نمایش نام دامنه، صادرکننده، تاریخ اعتبار و اثرانگشت SHA-256.
- بررسی تطابق کلید و گواهی؛ مرتب‌سازی زنجیره با بررسی امضای ارتباط صادرکننده.
- رمزگذاری پیش‌فرض کلیدهای خروجی و PFX؛ حالت سازگاری PFX برای سامانه‌های قدیمی.
- جلوگیری از جایگزینی فایل ورودی و درخواست تأیید برای بازنویسی خروجی موجود.
- پاک شدن فیلدهای رمز پس از تبدیل موفق یا بستن برنامه.

### روش استفاده

1. فایل صادرشده، مثلاً `certificate.cer` یا `certificate.pem`، را در **Certificate** انتخاب کنید.
2. اگر ورودی رمز دارد، **Input password** را وارد و **Inspect certificate** را بزنید.
3. برای PFX/P12 یا خروجی کلید، کلید خصوصی اصلی را در **Private key** انتخاب کنید. اگر داخل PFX یا PEM ورودی موجود باشد، نیاز به انتخاب جداگانه نیست.
4. فایل‌های واسط یا ریشه را در **CA chain → Add** اضافه کنید. برای بسته‌های چندگواهی، گواهی را در فهرست انتخاب کنید؛ وجود کلید خصوصی، گواهی منطبق را خودکار انتخاب می‌کند.
5. خروجی‌ها، پوشه و نام فایل را تعیین کنید. برای خروجی رمزدار، رمز خروجی و تکرارش را وارد کنید.
6. **Convert & save** را بزنید. فایل‌ها فقط در پوشه انتخاب‌شده نوشته می‌شوند.

**گواهی CER/PEM به‌تنهایی کلید خصوصی ندارد.** برای PFX سرور، کلیدی لازم است که هنگام ساخت CSR ایجاد شده است. کلید خصوصی از گواهی بازسازی نمی‌شود. اگر کلید و PFX ورودی رمزهای متفاوتی دارند، ابتدا گواهی را جداگانه به PEM خروجی بگیرید و سپس PEM و کلید را با رمز کلید وارد کنید.

### پسوندهای رایج و تفاوت آن‌ها

| پسوند / نام | کاربرد | پشتیبانی نسخه اول |
|---|---|---|
| `.pem` | متن Base64 با بلوک‌های BEGIN/END؛ می‌تواند گواهی، زنجیره یا کلید باشد | ورود و خروج؛ خروجی گواهی، زنجیره کامل یا ترکیبی |
| `.crt`, `.cer` | گواهی X.509؛ ممکن است PEM یا DER باشد | ورود هر دو؛ خروجی CRT/PEM و CER/PEM یا CER/DER |
| `.der` | کدگذاری باینری | ورود و خروج گواهی؛ ورود کلید از فیلد کلید |
| `.pfx`, `.p12` | بسته PKCS#12، شامل کلید خصوصی و گواهی و زنجیره اختیاری | ورود و خروج رمزدار |
| `.p7b`, `.p7c` | بسته PKCS#7 گواهی‌ها؛ بدون کلید خصوصی | ورود؛ خروجی DER و P7B/PEM |
| `.key` | نام رایج فایل کلید خصوصی، فرمت وابسته به محتوا | ورود PEM/DER؛ خروجی PKCS#8/PEM |
| `.pk8`, `.p8` | کلید خصوصی PKCS#8 | ورود از فیلد کلید؛ خروجی `.pk8` با DER |
| `.ca-bundle`, `.bundle` | نام قراردادی زنجیره گواهی‌ها با PEM | ورود؛ خروجی `.ca-bundle` |
| `fullchain.pem` | نام قراردادی گواهی اصلی همراه زنجیره PEM | خروجی `.fullchain.pem` |
| `.csr`, `.p10`, `.req` | درخواست امضای گواهی پیش از صدور | مرجع؛ تولید نمی‌شود |
| `.crl` | فهرست ابطال امضاشده توسط CA | مرجع؛ تولید نمی‌شود |
| `.jks`, `.keystore`, `.jceks` | مخزن کلید و گواهی Java | مرجع؛ نیازمند ابزار Java |
| `.p7m`, `.p7s` | پیام CMS یا امضا | مرجع؛ تبدیل ساده گواهی نیست |
| `.spc` | نام قدیمی ظرف گواهی، اغلب PKCS#7 | فقط اگر محتوای آن از فرمت‌های پشتیبانی‌شده باشد |

تغییر نام پسوند، تبدیل فرمت نیست. CSR، CRL، مخزن Java و امضای پیام، کاربردها و داده‌های متفاوتی دارند. [مستندات OpenSSL](https://docs.openssl.org/master/man1/openssl-format-options/) و [مستندات Cryptography](https://cryptography.io/en/50.0.2/hazmat/primitives/asymmetric/serialization/) تفاوت کدگذاری‌ها و ظرف‌ها را توضیح می‌دهند.

### حریم خصوصی و حدود بررسی

برنامه هیچ کد شبکه، آپلود، تله‌متری یا بررسی آنلاین ابطال ندارد. رمزها در فایل تنظیمات یا لاگ ذخیره نمی‌شوند. خروجی کلید به‌صورت پیش‌فرض رمزگذاری می‌شود. خاموش کردن این گزینه برای خروجی کلید، تأیید جداگانه می‌خواهد. پوشه‌های همگام‌شونده با OneDrive و سرویس‌های مشابه ممکن است توسط خود آن سرویس آپلود شوند؛ برای فایل‌های حساس، پوشه محلی انتخاب کنید.

این ابزار تبدیل است. اعتماد به CA، نام میزبان، ابطال و کامل بودن زنجیره نسبت به trust store سیستم را اعتبارسنجی نمی‌کند. زنجیره ناقص را فقط تا گواهی‌های ارائه‌شده می‌سازد و گواهی واسط گمشده را دانلود نمی‌کند. Python تضمین پاک کردن رمز از حافظه را نمی‌دهد؛ پاک کردن فیلد با پاک‌سازی قطعی حافظه متفاوت است. رمزگذاری فایل جایگزین حفاظت از کامپیوتر و کنترل دسترسی نیست.

## English

**mohamadmilad hadad — SSL Certificate Studio** is a local Python/Tkinter desktop converter for SSL/TLS certificates. Bring the PEM or CER files delivered by your certificate authority and export the formats your server needs. The Windows executable bundles its runtime and crypto libraries; Python and OpenSSL do not need to be installed on the user's computer.

### Download & use

Download **mohamadmilad hadad.exe** from [v1.0.0 Releases](https://github.com/Developesar/offline-ssl-certificate-studio/releases/tag/v1.0.0). `SHA256SUMS.txt` lists its checksum. No installer or administrator access is required. The first release is not publisher-signed.

Select the certificate, its original private key when required, and any issuer certificates. Enter the input password for encrypted sources, inspect the certificate, select output formats, choose a local folder and set an output password. Click **Convert & save**.

**A certificate cannot recreate its private key.** PFX/P12 exports require the matching original private key, either in the source bundle or provided separately. The key selects its matching certificate automatically. If an encrypted PFX and a separate encrypted key use different passwords, export the certificate to PEM first, then use that PEM and the key with its own password.

### Supported conversions

| Group | Output choices |
|---|---|
| Single certificate | PEM, CRT/PEM, CER/PEM, CER/DER, DER |
| Certificate chains | Full chain PEM, CA bundle PEM (without leaf) |
| PKCS#7 | P7B/DER, P7C/DER, P7B/PEM |
| PKCS#12 | Password-protected PFX, P12; modern or legacy-compatible encryption |
| Private key | PKCS#8 PEM `.key`, PKCS#8 DER `.pk8` |
| Combined PEM | Selected certificate, chain and private key |
| Public key | SubjectPublicKeyInfo PEM |

Input detection supports PEM/DER X.509, PEM/DER PKCS#7, and PKCS#12 regardless of filename. Private-key input supports PEM/DER and encrypted PKCS#8. Multiple output choices can be saved in one operation. Certificate/key matching and issuer signature checks prevent common packaging mistakes. Existing outputs require confirmation; input files are protected from replacement. Each output is staged locally and committed atomically, though a multi-file export is not a filesystem-wide transaction.

CSR (`.csr`, `.p10`, `.req`), CA-signed revocation lists (`.crl`), Java keystores (`.jks`, `.jceks`, `.keystore`) and CMS messages/signatures (`.p7m`, `.p7s`) are reference formats, **not exports in v1.0.0**.

### Privacy model

- Application code makes no network requests, uploads, telemetry calls or online revocation lookups.
- Passwords are not written to settings or logs. Password fields clear after a successful export.
- Private-key exports are encrypted by default; unencrypted key exports require confirmation. PFX/P12 exports always require a password.
- Choose a local, non-synced folder if you do not want other software to upload outputs.
- This is a converter, not a full TLS validator. It does not establish CA trust, hostname validity, revocation status or chain completeness against an OS trust store.
- Clearing a field does not guarantee secret erasure from Python process memory. File encryption does not replace machine security and access control. Legacy PFX uses older 3DES/SHA-1 compatibility options.

### Run from source

Use Python 3.11+ with Tkinter (included in the standard Windows Python installer):

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python app.py
```

Dependency installation needs Internet access or a local package cache. **The installed application itself runs offline.** `Pillow` is only needed to generate the icon; `PyInstaller` is only needed to build the EXE.

### Test & build

```powershell
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
.\build.ps1
```

The executable is written to `dist/mohamadmilad hadad.exe`. Tests use freshly generated synthetic certificates and temporary keys, not user files. CI tests contributions on Linux and Windows and builds a Windows artifact. Build scripts and source are included so forks can create their own releases.

### Contribute / توسعه نسخه‌های بعدی

Fork this repository, create a branch, make your change, run the tests and open a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md), [the changelog](CHANGELOG.md) and [security reporting](SECURITY.md). Ideas for later versions include full Persian RTL UI, Java keystore support, drag-and-drop and certificate-path validation. These are roadmap ideas, not current features.

برای توسعه، مخزن را **Fork** کنید، یک شاخه بسازید، تغییرات و تست‌ها را اضافه کنید و **Pull Request** بفرستید. گزارش ایراد و پیشنهاد قابلیت در Issues پذیرفته می‌شود. هرگز کلید خصوصی، گواهی واقعی سازمان یا رمز را در Issue و PR قرار ندهید.

Licensed under [MIT](LICENSE). Created by **mohamadmilad hadad**.
