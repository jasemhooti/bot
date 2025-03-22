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

# ایجاد محیط مجازی
python3 -m venv venv
source venv/bin/activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# ایجاد فایل تنظیمات
cat > config/settings.py << EOL
BOT_TOKEN = "$BOT_TOKEN"
ADMIN_ID = $ADMIN_ID
DOMAIN = "$DOMAIN"
DATABASE_URL = "postgresql://$DB_USER:$DB_PASS@localhost/netbox_bot"
EOL

# تنظیم Nginx
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
rm /etc/nginx/sites-enabled/default
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