#!/bin/bash

# رنگ‌ها برای خروجی
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}به نصب کننده ربات نت باکس خوش آمدید${NC}"

# بررسی سیستم عامل
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VERSION=$VERSION_ID
else
    echo -e "${RED}خطا در تشخیص سیستم عامل${NC}"
    exit 1
fi

# نصب پیش‌نیازها
echo -e "${YELLOW}در حال نصب پیش‌نیازها...${NC}"
apt-get update
apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx

# ایجاد کاربر دیتابیس
echo -e "${YELLOW}در حال تنظیم دیتابیس...${NC}"
read -p "نام کاربری دیتابیس را وارد کنید: " DB_USER
read -s -p "رمز عبور دیتابیس را وارد کنید: " DB_PASS
echo

# ایجاد دیتابیس
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -c "CREATE DATABASE netbox_bot;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE netbox_bot TO $DB_USER;"

# دریافت تنظیمات ربات
read -p "توکن ربات تلگرام را وارد کنید: " BOT_TOKEN
read -p "شناسه عددی ادمین را وارد کنید: " ADMIN_ID
read -p "دامنه سایت را وارد کنید: " DOMAIN

# ایجاد ساختار پوشه‌ها
mkdir -p config database handlers utils

# ایجاد فایل requirements.txt
cat > requirements.txt << EOL
python-telegram-bot==20.7
requests==2.31.0
python-dotenv==1.0.0
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9
aiohttp==3.9.1
python-jose==3.3.0
cryptography==41.0.7
EOL

# ایجاد فایل settings.py
cat > config/settings.py << EOL
import os
from dotenv import load_dotenv

load_dotenv()

# تنظیمات اصلی
BOT_TOKEN = "$BOT_TOKEN"
ADMIN_ID = $ADMIN_ID
DOMAIN = "$DOMAIN"

# تنظیمات دیتابیس
DATABASE_URL = "postgresql://$DB_USER:$DB_PASS@localhost/netbox_bot"

# تنظیمات X-UI
XUI_PANELS = [
    {
        'url': os.getenv('XUI_PANEL_URL', ''),
        'username': os.getenv('XUI_USERNAME', ''),
        'password': os.getenv('XUI_PASSWORD', '')
    }
]

# تنظیمات پرداخت
PAYMENT_METHODS = {
    'crypto': True,
    'bank_transfer': True,
    'card_number': os.getenv('CARD_NUMBER', '')
}

# تنظیمات بازی
GAME_SETTINGS = {
    'min_bet': 500,
    'max_bet': 5000000,
    'min_withdraw': 50000,
    'withdraw_time': 4  # ساعت
}

# تنظیمات سیستم
SYSTEM_SETTINGS = {
    'auto_approve_time': 5,  # دقیقه
    'backup_enabled': True,
    'backup_channel': os.getenv('BACKUP_CHANNEL', ''),
    'ticket_system': True,
    'referral_system': True,
    'referral_percentage': 10,
    'force_join_channel': True,
    'channel_username': os.getenv('CHANNEL_USERNAME', ''),
    'report_channel': os.getenv('REPORT_CHANNEL', '')
}

# تنظیمات کانفیگ
CONFIG_SETTINGS = {
    'auto_renew': True,
    'allow_name_change': True,
    'allow_link_change': True,
    'show_usage': True,
    'show_daily_usage': True,
    'show_weekly_usage': True
}
EOL

# ایجاد محیط مجازی
python3 -m venv venv
source venv/bin/activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# تنظیم Nginx
if [ -f /etc/nginx/sites-enabled/netbox-bot ]; then
    rm /etc/nginx/sites-enabled/netbox-bot
fi

if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
fi

cat > /etc/nginx/sites-available/netbox-bot << EOL
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOL

ln -s /etc/nginx/sites-available/netbox-bot /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

# ایجاد سرویس سیستم
cat > /etc/systemd/system/netbox-bot.service << EOL
[Unit]
Description=NetBox Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/netbox-bot
Environment=PYTHONPATH=/root/netbox-bot
ExecStart=/root/netbox-bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

systemctl daemon-reload
systemctl enable netbox-bot
systemctl start netbox-bot

echo -e "${GREEN}نصب با موفقیت به پایان رسید!${NC}"
echo -e "${YELLOW}اطلاعات نصب:${NC}"
echo -e "نام کاربری دیتابیس: $DB_USER"
echo -e "نام دیتابیس: netbox_bot"
echo -e "دامنه: $DOMAIN"
echo -e "شناسه ادمین: $ADMIN_ID" 