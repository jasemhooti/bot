# ربات تلگرامی نت باکس

ربات فروش کانفیگ VPN با قابلیت‌های پیشرفته مدیریت و بازی

## ویژگی‌های اصلی

- فروش خودکار کانفیگ VPN
- اتصال به پنل‌های X-UI
- سیستم مدیریت کاربران
- سیستم بازی آنلاین
- سیستم زیرمجموعه‌گیری
- سیستم تیکتینگ
- مدیریت موجودی
- سیستم پرداخت
- پشتیبان‌گیری خودکار

## پیش‌نیازها

- Python 3.8+
- PostgreSQL
- سرور Ubuntu

## نصب

برای نصب ربات، دستور زیر را در سرور اجرا کنید:

```bash
bash <(curl -s https://raw.githubusercontent.com/yourusername/netbox-bot/main/install.sh)
```

## تنظیمات

پس از نصب، موارد زیر را تنظیم کنید:
1. توکن ربات تلگرام
2. شناسه عددی ادمین
3. تنظیمات دیتابیس
4. تنظیمات پنل X-UI

## ساختار پروژه

```
netbox-bot/
├── config/
│   ├── __init__.py
│   └── settings.py
├── database/
│   ├── __init__.py
│   ├── models.py
│   └── database.py
├── handlers/
│   ├── __init__.py
│   ├── admin.py
│   ├── user.py
│   └── game.py
├── utils/
│   ├── __init__.py
│   ├── xui.py
│   └── helpers.py
├── install.sh
├── main.py
└── requirements.txt
```

## مجوز

MIT License 