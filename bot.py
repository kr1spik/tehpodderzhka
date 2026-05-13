import telebot
from telebot import types, apihelper
import time
from config import TOKEN, ADMIN_IDS
import logic
import note
import admin
import ui

apihelper.CONNECT_TIMEOUT = 30
apihelper.READ_TIMEOUT = 30

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

@bot.message_handler(commands=['start'])
def start(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    logic.init_db()
    welcome_text = f"<b>Привет, {message.from_user.first_name}!</b>\nЯ бот поддержки магазина."
    bot.send_message(message.chat.id, welcome_text, reply_markup=ui.get_main_keyboard(message.from_user.id))

@bot.message_handler(commands=['cancel'])
def cancel(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    bot.send_message(message.chat.id, "❌ Действие отменено.", reply_markup=ui.get_main_keyboard(message.from_user.id))

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
        types.InlineKeyboardButton("🚫 Отмена заказа", callback_data="sup_cancel"),
        types.InlineKeyboardButton("🔄 Возврат товара", callback_data="sup_return"),
        types.InlineKeyboardButton("🤝 Сотрудничество", callback_data="sup_b2b")
    )
    bot.send_message(message.chat.id, "<b>С каким отделом вы хотите связаться?</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('sup_'))
def ask_issue(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    depts = {"sup_dev": "Программисты", "sup_sales": "Отдел продаж", "sup_return": "Возврат товара", "sup_cancel": "Отмена заказа", "sup_b2b": "Сотрудничество"}
    dept_name = depts.get(call.data)
    
    cancel_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_markup.add(types.KeyboardButton("❌ Отмена"))
    
    msg = bot.send_message(call.message.chat.id, f"<b>Отдел: {dept_name}</b>\nНапишите ваше обращение:", reply_markup=cancel_markup)
    bot.register_next_step_handler(msg, finalize_ticket, dept_name)
    bot.answer_callback_query(call.id)

def finalize_ticket(message, dept):
    if message.text == "❌ Отмена":
        bot.send_message(message.chat.id, "Заявка отменена.", reply_markup=ui.get_main_keyboard(message.from_user.id))
        return

    ticket_id = logic.save_ticket(message.from_user.id, message.from_user.username, message.from_user.first_name, dept, message.text)
    
    if ticket_id:
        bot.send_message(message.chat.id, "✅ Заявка принята!", reply_markup=ui.get_main_keyboard(message.from_user.id))
        note.send_new_ticket_notification(bot, ticket_id, message.from_user.first_name, dept, message.text)
    else:
        bot.send_message(message.chat.id, "❌ Ошибка базы.", reply_markup=ui.get_main_keyboard(message.from_user.id))

if __name__ == "__main__":
    logic.init_db()
    admin.register_admin_handlers(bot) # Регистрация админских функций

    try:
        info = bot.get_me()
        print(f"--- Бот @{info.username} запущен! ---")
    except Exception as e:
        print(f"Ошибка запуска: {e}")

    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=40)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)