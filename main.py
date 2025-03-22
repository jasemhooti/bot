import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config.settings import BOT_TOKEN
from database.database import init_db
from handlers import admin, user, game

# تنظیم لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    """دستور شروع"""
    user = update.effective_user
    await update.message.reply_text(
        f'سلام {user.first_name}! به ربات نت باکس خوش آمدید.\n'
        'برای مشاهده منو از دکمه زیر استفاده کنید.',
        reply_markup=user.get_main_keyboard()
    )

async def help(update: Update, context):
    """دستور راهنما"""
    await update.message.reply_text(
        'راهنمای استفاده از ربات:\n'
        '1. برای خرید کانفیگ از منوی اصلی گزینه خرید را انتخاب کنید\n'
        '2. برای مشاهده کانفیگ‌های خود از منوی اصلی گزینه کانفیگ‌های من را انتخاب کنید\n'
        '3. برای شارژ حساب از منوی اصلی گزینه شارژ حساب را انتخاب کنید\n'
        '4. برای بازی از منوی اصلی گزینه بازی را انتخاب کنید\n'
        '5. برای پشتیبانی از منوی اصلی گزینه تیکت پشتیبانی را انتخاب کنید'
    )

def main():
    """تابع اصلی"""
    # ایجاد اپلیکیشن
    application = Application.builder().token(BOT_TOKEN).build()

    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    
    # هندلرهای ادمین
    application.add_handler(CommandHandler("admin", admin.admin_panel))
    application.add_handler(CallbackQueryHandler(admin.handle_admin_callback, pattern="^admin_"))
    
    # هندلرهای کاربر
    application.add_handler(CallbackQueryHandler(user.handle_user_callback, pattern="^user_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user.handle_message))
    
    # هندلرهای بازی
    application.add_handler(CallbackQueryHandler(game.handle_game_callback, pattern="^game_"))
    
    # شروع ربات
    application.run_polling()

if __name__ == '__main__':
    # ایجاد جداول دیتابیس
    init_db()
    # اجرای ربات
    main() 