# Contributing / مشارکت

Contributions and forks are welcome. This first version is intentionally small: `converter.py` handles local cryptographic conversions and `app.py` contains the Tkinter interface.

1. Fork the repository and create a descriptive branch.
2. Use Python 3.11+ and install `requirements.txt` in a virtual environment.
3. Keep processing local. Do not add uploads, analytics, automatic remote validation or network-based dependencies at runtime.
4. Add meaningful conversion tests for behavior changes. Use generated test certificates and temporary files only.
5. Run `python -m unittest discover -s tests -v`. For UI changes, check Windows at normal and enlarged display scaling.
6. Open a pull request explaining the problem, behavior and verification. Update Persian and English documentation when behavior changes.

Never commit real certificates, private keys, passwords or customer data. Certificate and key extensions are ignored as a precaution, but inspect your changes before publishing. Generated test keys must remain temporary.

## فارسی

فورک کنید، شاخه بسازید، تغییرتان را پیاده کنید و تست‌ها را اجرا کنید؛ سپس Pull Request بفرستید. برای قابلیت جدید مستندات فارسی و انگلیسی را به‌روز کنید. رفتار آفلاین برنامه باید حفظ شود. از اطلاعات واقعی کاربر در تست‌ها، Issue و PR استفاده نکنید.
