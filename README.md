# Google Region Checker

ابزار خط‌فرمان (CLI) پایتون برای بررسی این‌که سرویس‌های مختلف گوگل از شبکه‌ی فعلی شما در دسترس هستند یا نه — و تلاش برای حدس منطقی این‌که مشکل، **مسدودسازی شبکه‌ای** است یا **محدودیت منطقه‌ای/سیاست ارائه‌دهنده**.

> ⚠️ این ابزار فقط بر اساس سیگنال‌های شبکه (DNS، اتصال HTTPS، کد وضعیت HTTP، ریدایرکت، و متن پاسخ) نتیجه‌گیری می‌کند و **قطعیت صد‌درصد ندارد**. برای مثال گوگل به‌صورت رسمی ایران را در فهرست مناطق پشتیبانی‌شده‌ی Gemini API/AI Studio قرار نداده، اما دلیل دقیقِ در دسترس نبودن هر سرویس می‌تواند فرق داشته باشد (تحریم، فیلترینگ داخلی، یا هر دو).

## نمایش نمونه

```
╔══════════════════════════════════════╗
║        Google Region Checker          ║
╚══════════════════════════════════════╝

🌐 Public IP: 5.x.x.x
📍 Country:   Iran (IR)
🏙️  City:      Tehran
🏢 ISP:       ...

Checking Google services...

✓ Google Search        AVAILABLE
✓ Gmail                AVAILABLE
✓ Google Drive         AVAILABLE
✗ Gemini               RESTRICTED
✗ AI Studio            RESTRICTED
✗ Gemini API           RESTRICTED
✓ YouTube              AVAILABLE
✗ Google Workspace     RESTRICTED

──────────────────────────────────────
Summary
──────────────────────────────────────

Restricted services: 4/8

Possible reason:
🌍 Regional availability / provider policy

Confidence: 87%
```

## نصب

```bash
git clone https://github.com/MhdiTaheri/google-region-checker.git
cd google-region-checker
pip install -r requirements.txt
```

نیازمندی‌ها: پایتون ۳.10 یا بالاتر (به‌خاطر type hint هایی مثل `str | None`).

## استفاده

```bash
python main.py                 # گزارش رنگی در ترمینال
python main.py --json          # همان گزارش + خروجی report.json
python main.py --json out.json # ذخیره‌ی JSON با نام دلخواه
python main.py --quiet         # بدون خط‌های زنده‌ی "Checking..."
```

کد خروجی برنامه (`exit code`) هم معنادار است: اگر همه‌چیز `AVAILABLE` باشد `0`، در غیر این صورت `1` برمی‌گردد — مناسب برای استفاده در اسکریپت یا CI.

## این ابزار دقیقاً چه کاری انجام می‌دهد؟

برای هر سرویس (فهرست کامل در `config.py`)، این مراحل به‌ترتیب اجرا می‌شود:

1. **DNS resolution** — آیا دامنه اصلاً resolve می‌شود؟
2. **اتصال HTTPS** — آیا handshake و اتصال برقرار می‌شود؟
3. **کد وضعیت HTTP** — چه پاسخی برمی‌گردد؟
4. **بررسی متن پاسخ** — آیا عبارات شناخته‌شده‌ی «not available in your country» و مشابه آن دیده می‌شود؟
5. **بررسی ریدایرکت** — آیا به دامنه‌ی *نامرتبط* دیگری (مثلاً صفحه‌ی بلاک ISP) هدایت شده؟ ریدایرکت به زیردامنه‌های خودِ گوگل (مثل `accounts.google.com` برای صفحه‌ی ورود Gmail/Drive/Workspace) طبیعی است و «در دسترس» حساب می‌شود، نه بلاک.
6. **طبقه‌بندی نهایی** بر اساس ترکیب سیگنال‌های بالا، به یکی از این وضعیت‌ها:

| وضعیت | معنی |
|---|---|
| `AVAILABLE` | سرویس در دسترس است |
| `BLOCKED` | نشانه‌های مسدودسازی شبکه‌ای (DNS/IP/TLS) |
| `REGION_RESTRICTED` | نشانه‌ی محدودیت منطقه‌ای/سیاست ارائه‌دهنده |
| `CONNECTION_ERROR` | تایم‌اوت یا خطای نامشخص شبکه |
| `UNKNOWN` | داده کافی برای نتیجه‌گیری وجود ندارد |

هر نتیجه یک عدد **confidence (۰ تا ۱۰۰)** و یک دلیل انسانی‌خوان هم دارد — اینها هاردکد نیستند، بلکه از منطق `services/base.py::_classify()` بیرون می‌آیند.

## ساختار پروژه

```
google-region-checker/
│
├── main.py              # نقطه‌ی ورود CLI
├── config.py             # لیست سرویس‌ها + نشانه‌های بلاک منطقه‌ای
│
├── services/
│   ├── base.py           # منطق اصلی طبقه‌بندی وضعیت (یک‌جا، مشترک)
│   ├── registry.py        # پیدا کردن config هر سرویس با کلیدش
│   ├── google_search.py, gmail.py, drive.py, gemini.py,
│   │   ai_studio.py, gemini_api.py, youtube.py, workspace.py
│   └── __init__.py        # run_all_checks()
│
├── network/
│   ├── ip.py              # IP عمومی + geolocation (ip-api.com / ipify.org)
│   ├── dns.py              # DNS resolution
│   └── http.py             # اتصال HTTPS، کد وضعیت، ریدایرکت
│
├── output/
│   ├── console.py          # گزارش رنگی ترمینال
│   └── json.py             # خروجی JSON ماشین‌خوان
│
├── tests/
│   └── test_classification.py   # تست منطق طبقه‌بندی (بدون نیاز به اینترنت)
│
├── requirements.txt
├── README.md
└── LICENSE
```

نکته‌ی معماری: هر فایل سرویس (`gmail.py`, `gemini.py`, ...) صرفاً یک wrapper نازک روی `services/base.py::check_service()` است. برای اضافه کردن یک سرویس گوگل جدید کافیست:
1. یک entry به `config.py` اضافه کنید.
2. یک فایل کوچک مثل بقیه در `services/` بسازید (یا حتی همان‌جا از `check_service()` مستقیم استفاده کنید).

هیچ لیست هاردکدشده‌ای برای این‌که «کدام سرویس در کدام کشور بلاک است» وجود ندارد — همه‌چیز runtime و بر اساس تست واقعی شبکه تعیین می‌شود.

## توسعه‌های آینده (پیشنهادی)

- [ ] رابط گرافیکی با Tkinter یا PySide6 و نمایش داشبورد
- [ ] اجرای موازی چک سرویس‌ها (`concurrent.futures`) برای سرعت بیشتر
- [ ] پشتیبانی از پروکسی/VPN برای مقایسه‌ی نتیجه با و بدون آن
- [ ] history/trend — ذخیره‌ی نتایج در طول زمان و رسم نمودار تغییرات

## اجرای تست‌ها

```bash
python tests/test_classification.py
```

## مجوز

MIT — به فایل [LICENSE](LICENSE) نگاه کنید.
