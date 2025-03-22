from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.database import get_db
from database.models import User, Config, Plan, Discount, Ticket
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

def get_main_keyboard():
    """منوی اصلی کاربر"""
    keyboard = [
        [
            InlineKeyboardButton("🛒 خرید کانفیگ", callback_data="user_buy"),
            InlineKeyboardButton("📱 کانفیگ‌های من", callback_data="user_configs")
        ],
        [
            InlineKeyboardButton("💰 شارژ حساب", callback_data="user_charge"),
            InlineKeyboardButton("🎮 بازی", callback_data="user_game")
        ],
        [
            InlineKeyboardButton("🎫 تیکت پشتیبانی", callback_data="user_ticket"),
            InlineKeyboardButton("👥 زیرمجموعه‌گیری", callback_data="user_referral")
        ],
        [
            InlineKeyboardButton("👤 پروفایل", callback_data="user_profile")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def handle_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش دکمه‌های کاربر"""
    query = update.callback_query
    await query.answer()

    action = query.data.split('_')[1]

    if action == "buy":
        await show_plans(query)
    elif action == "configs":
        await show_user_configs(query)
    elif action == "charge":
        await show_charge_options(query)
    elif action == "game":
        await show_game_menu(query)
    elif action == "ticket":
        await show_ticket_menu(query)
    elif action == "referral":
        await show_referral_info(query)
    elif action == "profile":
        await show_user_profile(query)

async def show_plans(query):
    """نمایش پلن‌های موجود"""
    db = next(get_db())
    plans = db.query(Plan).filter(Plan.is_active == True).all()
    
    text = "لیست پلن‌های موجود:\n\n"
    for plan in plans:
        text += f"نام: {plan.name}\n"
        text += f"حجم: {plan.volume} گیگابایت\n"
        text += f"مدت زمان: {plan.duration} روز\n"
        text += f"قیمت: {plan.price} تومان\n\n"

    keyboard = []
    for plan in plans:
        keyboard.append([InlineKeyboardButton(
            f"خرید {plan.name} - {plan.price} تومان",
            callback_data=f"user_buy_plan_{plan.id}"
        )])
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data="user_back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def show_user_configs(query):
    """نمایش کانفیگ‌های کاربر"""
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == query.from_user.id).first()
    
    if not user:
        await query.message.edit_text("خطا در یافتن اطلاعات کاربر")
        return

    configs = db.query(Config).filter(Config.user_id == user.id).all()
    
    if not configs:
        text = "شما هیچ کانفیگی ندارید."
    else:
        text = "لیست کانفیگ‌های شما:\n\n"
        for config in configs:
            text += f"نام: {config.name}\n"
            text += f"حجم: {config.volume} گیگابایت\n"
            text += f"تاریخ انقضا: {config.expiry_date}\n"
            text += f"وضعیت: {'فعال' if config.is_active else 'غیرفعال'}\n\n"

    keyboard = [
        [InlineKeyboardButton("بازگشت", callback_data="user_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def show_charge_options(query):
    """نمایش گزینه‌های شارژ حساب"""
    text = "روش‌های شارژ حساب:\n\n"
    text += "1. کارت به کارت\n"
    text += "2. ارز دیجیتال\n"
    text += "3. کد تخفیف"

    keyboard = [
        [InlineKeyboardButton("کارت به کارت", callback_data="user_charge_card")],
        [InlineKeyboardButton("ارز دیجیتال", callback_data="user_charge_crypto")],
        [InlineKeyboardButton("کد تخفیف", callback_data="user_charge_discount")],
        [InlineKeyboardButton("بازگشت", callback_data="user_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def show_game_menu(query):
    """نمایش منوی بازی"""
    text = "منوی بازی:\n\n"
    text += "1. بازی دو نفره\n"
    text += "2. بازی با ربات"

    keyboard = [
        [InlineKeyboardButton("بازی دو نفره", callback_data="user_game_multi")],
        [InlineKeyboardButton("بازی با ربات", callback_data="user_game_single")],
        [InlineKeyboardButton("بازگشت", callback_data="user_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def show_ticket_menu(query):
    """نمایش منوی تیکت"""
    text = "پشتیبانی:\n\n"
    text += "لطفاً موضوع تیکت خود را وارد کنید."

    keyboard = [
        [InlineKeyboardButton("بازگشت", callback_data="user_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def show_referral_info(query):
    """نمایش اطلاعات زیرمجموعه‌گیری"""
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == query.from_user.id).first()
    
    if not user:
        await query.message.edit_text("خطا در یافتن اطلاعات کاربر")
        return

    text = "اطلاعات زیرمجموعه‌گیری:\n\n"
    text += f"لینک دعوت شما: https://t.me/{context.bot.username}?start={user.id}\n"
    text += f"تعداد زیرمجموعه‌ها: {len(user.referrals)}\n"
    text += f"درصد پورسانت: {user.referral_percentage}%"

    keyboard = [
        [InlineKeyboardButton("بازگشت", callback_data="user_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def show_user_profile(query):
    """نمایش پروفایل کاربر"""
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == query.from_user.id).first()
    
    if not user:
        await query.message.edit_text("خطا در یافتن اطلاعات کاربر")
        return

    text = "پروفایل شما:\n\n"
    text += f"نام: {user.first_name} {user.last_name}\n"
    text += f"یوزرنیم: @{user.username}\n"
    text += f"موجودی: {user.balance} تومان\n"
    text += f"تاریخ ثبت نام: {user.created_at}\n"
    text += f"تعداد کانفیگ‌ها: {len(user.configs)}\n"
    text += f"تعداد زیرمجموعه‌ها: {len(user.referrals)}"

    keyboard = [
        [InlineKeyboardButton("بازگشت", callback_data="user_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام‌های کاربر"""
    message = update.message
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

    if not user:
        await message.reply_text("خطا در یافتن اطلاعات کاربر")
        return

    # پردازش پیام‌های تیکت
    if user.current_state == "ticket_subject":
        ticket = Ticket(
            user_id=user.id,
            subject=message.text,
            status="open"
        )
        db.add(ticket)
        db.commit()
        user.current_state = None
        await message.reply_text("تیکت شما با موفقیت ثبت شد. به زودی پاسخ داده خواهد شد.")
        return

    # پردازش پیام‌های بازی
    if user.current_state == "game_bet":
        try:
            bet_amount = float(message.text)
            if bet_amount < GAME_SETTINGS['min_bet']:
                await message.reply_text(f"حداقل مبلغ شرط {GAME_SETTINGS['min_bet']} تومان است.")
                return
            if bet_amount > GAME_SETTINGS['max_bet']:
                await message.reply_text(f"حداکثر مبلغ شرط {GAME_SETTINGS['max_bet']} تومان است.")
                return
            if bet_amount > user.balance:
                await message.reply_text("موجودی شما کافی نیست.")
                return
            # ادامه پردازش بازی
        except ValueError:
            await message.reply_text("لطفاً یک عدد معتبر وارد کنید.")
            return 