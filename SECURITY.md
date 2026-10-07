# Security / امنیت

Please use GitHub private vulnerability reporting through the repository's Security tab when enabled. Do not publish exploitable details or secrets in a public issue. Reports should describe the affected version, a synthetic reproduction and the impact.

The application never needs your production private key or password to diagnose a bug. Reproduce issues using generated test certificates. No runtime network access is part of the project's design.

This v1.0.0 release has conversion tests but has not received an independent security audit. It converts certificate material; it does not validate trust or revocation. Review the source and protect the host and output files.

برای گزارش آسیب‌پذیری از بخش گزارش خصوصی در Security استفاده کنید. رمز و کلید واقعی را ارسال نکنید. نسخه اول ممیزی امنیتی مستقل ندارد؛ تست‌های تبدیل جایگزین ممیزی نیستند.
