from telebot import types
from config import ADMIN_IDS

def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("❓ Помощь (FAQ)", "🛠 Поддержка")
    
    # Кнопка появится только у тех, чей ID в списке ADMIN_IDS
    if user_id in ADMIN_IDS:
        markup.row("👔 Панель сотрудника")
        
    return markup