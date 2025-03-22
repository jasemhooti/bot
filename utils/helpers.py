import os
import json
from datetime import datetime, timedelta
from database.database import get_db
from database.models import User, Config, UsageLog

def format_bytes(bytes):
    """تبدیل بایت به فرمت خوانا"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} PB"

def format_duration(days):
    """تبدیل روز به فرمت خوانا"""
    if days < 30:
        return f"{days} روز"
    months = days // 30
    remaining_days = days % 30
    if remaining_days == 0:
        return f"{months} ماه"
    return f"{months} ماه و {remaining_days} روز"

def generate_config_link(config_data):
    """تولید لینک کانفیگ"""
    protocol = config_data.get('protocol', 'vless')
    uuid = config_data.get('settings', {}).get('clients', [{}])[0].get('id', '')
    host = config_data.get('listen', '')
    port = config_data.get('port', 0)
    
    if protocol == 'vless':
        return f"vless://{uuid}@{host}:{port}?encryption=none&type=tcp#config"
    return None

def backup_database():
    """پشتیبان‌گیری از دیتابیس"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_{timestamp}.sql"
        
        # اجرای دستور pg_dump
        os.system(f"pg_dump -U {os.getenv('DB_USER')} -d netbox_bot > {backup_file}")
        
        return backup_file
    except Exception as e:
        print(f"خطا در پشتیبان‌گیری: {str(e)}")
        return None

def restore_database(backup_file):
    """بازیابی دیتابیس"""
    try:
        # اجرای دستور psql
        os.system(f"psql -U {os.getenv('DB_USER')} -d netbox_bot < {backup_file}")
        return True
    except Exception as e:
        print(f"خطا در بازیابی: {str(e)}")
        return False

def update_config_usage(config_id, usage_bytes):
    """بروزرسانی مصرف کانفیگ"""
    db = next(get_db())
    config = db.query(Config).filter(Config.id == config_id).first()
    
    if not config:
        return False
    
    # اضافه کردن لاگ مصرف
    usage_log = UsageLog(
        config_id=config_id,
        usage=usage_bytes / (1024 * 1024 * 1024)  # تبدیل به گیگابایت
    )
    db.add(usage_log)
    
    # بروزرسانی حجم باقیمانده
    config.volume -= usage_bytes / (1024 * 1024 * 1024)
    
    if config.volume <= 0:
        config.is_active = False
    
    db.commit()
    return True

def get_user_stats(user_id):
    """دریافت آمار کاربر"""
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    # محاسبه آمار
    total_configs = len(user.configs)
    active_configs = len([c for c in user.configs if c.is_active])
    total_games = len(user.games)
    won_games = len([g for g in user.games if g.result == "win"])
    lost_games = len([g for g in user.games if g.result == "lose"])
    
    return {
        'total_configs': total_configs,
        'active_configs': active_configs,
        'total_games': total_games,
        'won_games': won_games,
        'lost_games': lost_games,
        'win_rate': (won_games / total_games * 100) if total_games > 0 else 0
    }

def get_daily_usage(config_id):
    """دریافت مصرف روزانه کانفیگ"""
    db = next(get_db())
    today = datetime.now().date()
    
    usage_logs = db.query(UsageLog).filter(
        UsageLog.config_id == config_id,
        UsageLog.date >= today
    ).all()
    
    total_usage = sum(log.usage for log in usage_logs)
    return total_usage

def get_weekly_usage(config_id):
    """دریافت مصرف هفتگی کانفیگ"""
    db = next(get_db())
    week_ago = datetime.now() - timedelta(days=7)
    
    usage_logs = db.query(UsageLog).filter(
        UsageLog.config_id == config_id,
        UsageLog.date >= week_ago
    ).all()
    
    total_usage = sum(log.usage for log in usage_logs)
    return total_usage 