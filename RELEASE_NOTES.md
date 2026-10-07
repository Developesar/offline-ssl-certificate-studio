# v1.0.0 — mohamadmilad hadad

First release of **Offline SSL Certificate Studio**.

## فارسی

اولین نسخه برنامه تبدیل آفلاین گواهی‌های SSL/TLS با نام **mohamadmilad hadad**.

- رابط Tkinter تیره، آیکون اختصاصی، راهنما و مستندات فارسی و انگلیسی.
- ۱۶ گزینه خروجی برای گواهی، زنجیره، PFX/P12، PKCS#7 و کلیدها.
- پردازش کامل روی کامپیوتر شما؛ بدون آپلود یا درخواست شبکه.
- رمزگذاری پیش‌فرض، بررسی تطابق کلید و گواهی و مرتب‌سازی زنجیره.
- مجوز MIT؛ آماده برای Fork و مشارکت از طریق Pull Request.

**دانلود:** فایل `mohamadmilad-hadad.exe` را اجرا کنید؛ نصب Python یا OpenSSL لازم نیست. هش فایل در `SHA256SUMS.txt` قرار دارد. فایل اجرایی امضای دیجیتال ناشر ندارد.

برای ساخت PFX قابل نصب روی سرور، کلید خصوصی اصلی گواهی لازم است. CSR، CRL و مخزن‌های Java خروجی‌های این نسخه نیستند. این ابزار اعتماد و ابطال گواهی را اعتبارسنجی نمی‌کند.

## English

- Standalone Windows x64 executable with bundled Python/Tkinter and cryptography.
- 16 export choices: X.509 PEM/DER, PKCS#7, PKCS#12, PEM chains, private and public keys.
- No runtime uploads, network requests, telemetry or password files.
- Key/certificate matching, issuer signature checks, encrypted exports and optional legacy PFX compatibility.
- MIT license, bilingual docs, synthetic conversion tests and contributor-friendly CI.

Download `mohamadmilad-hadad.exe` and run it locally. Verify the SHA-256 checksum against `SHA256SUMS.txt`. No Python or OpenSSL installation is required. This initial executable is not publisher-signed.

PFX/P12 needs the original matching private key. CSR, CRL and Java keystores are reference formats, not outputs in this release. Conversion does not establish CA trust or check revocation. Use a local, non-synced output folder for sensitive material.
