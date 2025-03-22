from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import ADMIN_ID
from database.database import get_db
from database.models import User, Config, Plan, Discount, Ticket
from sqlalchemy.orm import Session

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل ادمین"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return

    keyboard = [
        [
            InlineKeyboardButton("مدیریت پلن‌ها", callback_data="admin_plans"),
            InlineKeyboardButton("مدیریت تخفیف‌ها", callback_data="admin_discounts")
        ],
        [
            InlineKeyboardButton("مدیریت کاربران", callback_data="admin_users"),
            InlineKeyboardButton("گزارشات", callback_data="admin_reports")
        ],
        [
            InlineKeyboardButton("تیکت‌ها", callback_data="admin_tickets"),
            InlineKeyboardButton("تنظیمات", callback_data="admin_settings")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("پنل مدیریت:", reply_markup=reply_markup)

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش دکمه‌های ادمین"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.message.reply_text("شما دسترسی به این بخش را ندارید.")
        return

    action = query.data.split('_')[1]

    if action == "plans":
        await show_plans(query)
    elif action == "discounts":
        await show_discounts(query)
    elif action == "users":
        await show_users(query)
    elif action == "reports":
        await show_reports(query)
    elif action == "tickets":
        await show_tickets(query)
    elif action == "settings":
        await show_settings(query)

async def show_plans(query):
    """نمایش پلن‌ها"""
    db = next(get_db())
    plans = db.query(Plan).all()
    
    text = "لیست پلن‌ها:\n\n"
    for plan in plans:
        text += f"نام: {plan.name}\n"
        text += f"حجم: {plan.volume} گیگابایت\n"
        text += f"مدت زمان: {plan.duration} روز\n"
        text += f"قیمت: {plan.price} تومان\n"
        text += f"وضعیت: {'فعال' if plan.is_active else 'غیرفعال'}\n\n"

    keyboard = [
        [InlineKeyboardButton("افزودن پلن جدید", callback_data="admin_add_plan")],
        [InlineKeyboardButton("بازگشت", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def show_discounts(query):
    """نمایش تخفیف‌ها"""
    db = next(get_db())
    discounts = db.query(Discount).all()
    
    text = "لیست تخفیف‌ها:\n\n"
    for discount in discounts:
        text += f"کد: {discount.code}\n"
        text += f"درصد: {discount.percentage}%\n"
        text += f"وضعیت: {'فعال' if discount.is_active else 'غیرفعال'}\n"
        if discount.expiry_date:
            text += f"تاریخ انقضا: {discount.expiry_date}\n"
        text += "\n"

    keyboard = [
        [InlineKeyboardButton("افزودن تخفیف جدید", callback_data="admin_add_discount")],
        [InlineKeyboardButton("بازگشت", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def show_users(query):
    """نمایش کاربران"""
    db = next(get_db())
    users = db.query(User).all()
    
    text = "لیست کاربران:\n\n"
    for user in users:
        text += f"نام: {user.first_name} {user.last_name}\n"
        text += f"یوزرنیم: @{user.username}\n"
        text += f"موجودی: {user.balance} تومان\n"
        text += f"تاریخ ثبت نام: {user.created_at}\n"
        text += f"وضعیت: {'مسدود' if user.is_banned else 'فعال'}\n\n"

    keyboard = [
        [InlineKeyboardButton("بازگشت", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def show_reports(query):
    """نمایش گزارشات"""
    db = next(get_db())
    
    # آمار کلی
    total_users = db.query(User).count()
    total_configs = db.query(Config).count()
    total_tickets = db.query(Ticket).count()
    
    text = "گزارشات کلی:\n\n"
    text += f"تعداد کل کاربران: {total_users}\n"
    text += f"تعداد کل کانفیگ‌ها: {total_configs}\n"
    text += f"تعداد کل تیکت‌ها: {total_tickets}\n"

    keyboard = [
        [InlineKeyboardButton("بازگشت", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def show_tickets(query):
    """نمایش تیکت‌ها"""
    db = next(get_db())
    tickets = db.query(Ticket).filter(Ticket.status == "open").all()
    
    text = "تیکت‌های باز:\n\n"
    for ticket in tickets:
        text += f"موضوع: {ticket.subject}\n"
        text += f"کاربر: {ticket.user.first_name} {ticket.user.last_name}\n"
        text += f"تاریخ: {ticket.created_at}\n\n"

    keyboard = [
        [InlineKeyboardButton("بازگشت", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def show_settings(query):
    """نمایش تنظیمات"""
    text = "تنظیمات سیستم:\n\n"
    text += "1. تنظیمات عمومی\n"
    text += "2. تنظیمات پرداخت\n"
    text += "3. تنظیمات بازی\n"
    text += "4. تنظیمات پشتیبان‌گیری\n"

    keyboard = [
        [InlineKeyboardButton("بازگشت", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup) 