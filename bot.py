import telebot
from telebot import types, apihelper
import time
from config import TOKEN
import logic

apihelper.CONNECT_TIMEOUT = 30
apihelper.READ_TIMEOUT = 30

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("❓ Помощь (FAQ)", "🛠 Поддержка")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    logic.init_db()
    welcome_text = f"<b>Привет, {message.from_user.first_name}!</b>\nЯ бот поддержки магазина 'Продаем все на свете'."
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

@bot.message_handler(commands=['cancel'])
def cancel(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    bot.send_message(message.chat.id, "❌ Действие отменено. Вы вернулись в главное меню.", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "❓ Помощь (FAQ)")
def show_faq(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for question in logic.FAQ.keys():
        markup.add(types.InlineKeyboardButton(text=question.capitalize(), callback_data=f"faq_{question}"))
    bot.send_message(message.chat.id, "<b>Выберите вопрос:</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('faq_'))
def faq_answer(call):
    question_key = call.data.split("_")[1]
    answer = logic.get_faq_answer(question_key)
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_faq"))
    bot.edit_message_text(f"❓ <b>{question_key.capitalize()}</b>\n\n{answer}", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_faq")
def back_to_faq(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for question in logic.FAQ.keys():
        markup.add(types.InlineKeyboardButton(text=question.capitalize(), callback_data=f"faq_{question}"))
    bot.edit_message_text("<b>Выберите вопрос:</b>", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🛠 Поддержка")
def contact_support(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💻 Программисты", callback_data="sup_dev"),
        types.InlineKeyboardButton("📦 Отдел продаж", callback_data="sup_sales"),
        types.InlineKeyboardButton("🚫 Отмена/Изменение заказа", callback_data="sup_cancel"),
        types.InlineKeyboardButton("🔄 Возврат товара", callback_data="sup_return"),
        types.InlineKeyboardButton("🤝 Сотрудничество", callback_data="sup_b2b")
    )
    bot.send_message(message.chat.id, "<b>С каким отделом вы хотите связаться?</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('sup_'))
def ask_issue(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    depts = {
        "sup_dev": "Программисты",
        "sup_sales": "Отдел продаж",
        "sup_return": "Возврат товара",
        "sup_cancel": "Отмена заказа",
        "sup_b2b": "Сотрудничество"
    }
    dept_name = depts.get(call.data)
    
    cancel_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_markup.add(types.KeyboardButton("❌ Отмена"))
    
    msg = bot.send_message(call.message.chat.id, f"<b>Отдел: {dept_name}</b>\nНапишите ваше обращение или нажмите кнопку отмены:", reply_markup=cancel_markup)
    bot.register_next_step_handler(msg, finalize_ticket, dept_name)
    bot.answer_callback_query(call.id)

def finalize_ticket(message, dept):
    if message.text == "❌ Отмена":
        bot.send_message(message.chat.id, "Заявка отменена.", reply_markup=get_main_keyboard())
        return

    if not message.text:
        bot.send_message(message.chat.id, "❌ Нужно отправить текст.")
        return

    success = logic.save_ticket(message.from_user.id, message.from_user.username, message.from_user.first_name, dept, message.text)
    bot.send_message(message.chat.id, "✅ Заявка принята!", reply_markup=get_main_keyboard())

if __name__ == "__main__":
    logic.init_db()
    
    try:
        bot_info = bot.get_me()
        print(f"--- Бот успешно запущен! ---")
        print(f"Имя бота: {bot_info.first_name}")
        print(f"Username: @{bot_info.username}")
        print(f"ID: {bot_info.id}")
        print(f"Статус: Ожидание сообщений...")
        print(f"----------------------------")
    except Exception as e:
        print(f"Ошибка при получении данных о боте: {e}")

    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=40)
        except Exception as e:
            print(f"Сетевая ошибка: {e}. Повторный запуск через 5 секунд...")
            time.sleep(5)