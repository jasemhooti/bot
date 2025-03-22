import os
from dotenv import load_dotenv

load_dotenv()

# تنظیمات اصلی
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
DOMAIN = os.getenv('DOMAIN', 'localhost')

# تنظیمات دیتابیس
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/netbox_bot')

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