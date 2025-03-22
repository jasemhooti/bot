from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.database import get_db
from database.models import User, Game
from config.settings import GAME_SETTINGS
import random

# ذخیره وضعیت بازی‌های در حال انجام
active_games = {}

async def handle_game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش دکمه‌های بازی"""
    query = update.callback_query
    await query.answer()

    action = query.data.split('_')[1]

    if action == "multi":
        await show_multi_game_menu(query)
    elif action == "single":
        await show_single_game_menu(query)
    elif action == "start":
        await start_game(query)
    elif action == "guess":
        await handle_guess(query)
    elif action == "cancel":
        await cancel_game(query)
    elif action == "draw":
        await draw_game(query)

async def show_multi_game_menu(query):
    """نمایش منوی بازی دو نفره"""
    text = "بازی دو نفره:\n\n"
    text += "در این بازی هر بازیکن یک عدد از 1 تا 6 انتخاب می‌کند و بازیکن مقابل باید آن را حدس بزند.\n"
    text += f"حداقل مبلغ شرط: {GAME_SETTINGS['min_bet']} تومان\n"
    text += f"حداکثر مبلغ شرط: {GAME_SETTINGS['max_bet']} تومان"

    keyboard = [
        [InlineKeyboardButton("شروع بازی جدید", callback_data="game_start")],
        [InlineKeyboardButton("بازگشت", callback_data="user_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def show_single_game_menu(query):
    """نمایش منوی بازی با ربات"""
    text = "بازی با ربات:\n\n"
    text += "در این بازی ربات یک عدد از 1 تا 6 انتخاب می‌کند و شما باید آن را حدس بزنید.\n"
    text += f"حداقل مبلغ شرط: {GAME_SETTINGS['min_bet']} تومان\n"
    text += f"حداکثر مبلغ شرط: {GAME_SETTINGS['max_bet']} تومان"

    keyboard = [
        [InlineKeyboardButton("شروع بازی جدید", callback_data="game_start")],
        [InlineKeyboardButton("بازگشت", callback_data="user_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def start_game(query):
    """شروع بازی"""
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == query.from_user.id).first()
    
    if not user:
        await query.message.edit_text("خطا در یافتن اطلاعات کاربر")
        return

    if user.balance < GAME_SETTINGS['min_bet']:
        await query.message.edit_text("موجودی شما کافی نیست.")
        return

    # ایجاد بازی جدید
    game = Game(
        user_id=user.id,
        type="single" if "single" in query.data else "multi",
        bet_amount=GAME_SETTINGS['min_bet'],
        result="pending"
    )
    db.add(game)
    db.commit()

    # ذخیره اطلاعات بازی
    active_games[user.id] = {
        'game_id': game.id,
        'number': random.randint(1, 6),
        'type': game.type
    }

    text = "لطفاً عدد خود را از 1 تا 6 انتخاب کنید:"
    keyboard = []
    for i in range(1, 7):
        keyboard.append([InlineKeyboardButton(str(i), callback_data=f"game_guess_{i}")])
    keyboard.append([InlineKeyboardButton("انصراف", callback_data="game_cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def handle_guess(query):
    """پردازش حدس بازیکن"""
    user_id = query.from_user.id
    if user_id not in active_games:
        await query.message.edit_text("بازی یافت نشد.")
        return

    game_data = active_games[user_id]
    guessed_number = int(query.data.split('_')[2])
    correct_number = game_data['number']

    db = next(get_db())
    game = db.query(Game).filter(Game.id == game_data['game_id']).first()
    
    if not game:
        await query.message.edit_text("خطا در یافتن اطلاعات بازی")
        return

    if guessed_number == correct_number:
        # برنده شدن
        game.result = "win"
        user = db.query(User).filter(User.id == game.user_id).first()
        user.balance += game.bet_amount
        text = "تبریک! شما برنده شدید! 🎉"
    else:
        # باختن
        game.result = "lose"
        user = db.query(User).filter(User.id == game.user_id).first()
        user.balance -= game.bet_amount
        text = f"متأسفانه باختید! عدد صحیح {correct_number} بود."

    db.commit()
    del active_games[user_id]

    keyboard = [
        [InlineKeyboardButton("بازی مجدد", callback_data="game_start")],
        [InlineKeyboardButton("بازگشت به منو", callback_data="user_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup)

async def cancel_game(query):
    """لغو بازی"""
    user_id = query.from_user.id
    if user_id not in active_games:
        await query.message.edit_text("بازی یافت نشد.")
        return

    db = next(get_db())
    game = db.query(Game).filter(Game.id == active_games[user_id]['game_id']).first()
    
    if game:
        game.result = "cancelled"
        db.commit()

    del active_games[user_id]
    await query.message.edit_text("بازی لغو شد.")

async def draw_game(query):
    """مساوی کردن بازی"""
    user_id = query.from_user.id
    if user_id not in active_games:
        await query.message.edit_text("بازی یافت نشد.")
        return

    db = next(get_db())
    game = db.query(Game).filter(Game.id == active_games[user_id]['game_id']).first()
    
    if game:
        game.result = "draw"
        db.commit()

    del active_games[user_id]
    await query.message.edit_text("بازی مساوی شد.") 