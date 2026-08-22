from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from app.config import settings

def get_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Open WebApp", web_app=WebAppInfo(url=settings.WEBAPP_URL))],
        [InlineKeyboardButton(text="🔔 Daily Reminders", callback_data="toggle_reminder")]
    ])
