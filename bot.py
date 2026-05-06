import telebot
from telebot import types
from config import TOKEN
import logic

bot = telebot.TeleBot(TOKEN)

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("❓ Часто задаваемые вопросы"))
    markup.add(types.KeyboardButton("🛠 Связаться с поддержкой"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        f"Добро пожаловать в 'Продаем все на свете', {message.from_user.first_name}!\nЯ ваш автоматический помощник.",
        reply_markup=get_main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "❓ Часто задаваемые вопросы")
def show_faq_hint(message):
    bot.send_message(message.chat.id, "Просто напишите ваш вопрос (например: 'доставка' или 'возврат').")

@bot.message_handler(func=lambda m: m.text == "🛠 Связаться с поддержкой")
def support_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💻 Технический отдел (Сайт/Оплата)", callback_data="dept_dev"))
    markup.add(types.InlineKeyboardButton("📦 Отдел продаж (Товары/Доставка)", callback_data="dept_sales"))
    bot.send_message(message.chat.id, "Выберите отдел для обращения:", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    answer = logic.get_faq_answer(message.text)
    if answer:
        bot.send_message(message.chat.id, answer)
    else:
        bot.send_message(
            message.chat.id, 
            "К сожалению, я не нашел точного ответа. Воспользуйтесь кнопкой 'Связаться с поддержкой'.",
            reply_markup=get_main_menu()
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('dept_'))
def process_dept(call):
    dept_map = {"dept_dev": "Программисты", "dept_sales": "Отдел продаж"}
    dept_name = dept_map.get(call.data)
    msg = bot.send_message(call.message.chat.id, f"Вы выбрали: {dept_name}.\nПодробно опишите проблему в ОДНОМ сообщении:")
    bot.register_next_step_handler(msg, save_user_issue, dept_name)
    bot.answer_callback_query(call.id)

def save_user_issue(message, dept_name):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, "Пожалуйста, используйте только текст для описания проблемы.")
        return

    success = logic.save_ticket(message.from_user.id, message.from_user.username, dept_name, message.text)
    if success:
        bot.send_message(message.chat.id, "✅ Заявка №{} успешно создана. Ожидайте ответа специалиста.".format(message.message_id))
    else:
        bot.send_message(message.chat.id, "❌ Произошла ошибка при сохранении. Попробуйте позже.")

@bot.message_handler(content_types=['voice', 'video', 'photo'])
def handle_media(message):
    bot.send_message(message.chat.id, "Я пока не умею обрабатывать медиа-файлы. Пожалуйста, напишите текстом.")

if __name__ == "__main__":
    logic.init_db()
    bot.polling(none_stop=True)