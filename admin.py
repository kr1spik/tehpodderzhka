from telebot import types
import logic
import ui
from config import ADMIN_IDS
import sqlite3

def register_admin_handlers(bot):
    @bot.message_handler(func=lambda m: m.text == "👔 Панель сотрудника")
    def admin_panel(message):
        if message.from_user.id not in ADMIN_IDS:
            return

        conn = sqlite3.connect('support.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, first_name, department, issue FROM tickets WHERE status = "NEW"')
        tickets = cursor.fetchall()
        conn.close()

        if not tickets:
            bot.send_message(message.chat.id, "✅ Новых заявок нет!", reply_markup=ui.get_main_keyboard(message.from_user.id))
            return

        bot.send_message(message.chat.id, f"📂 <b>Новых заявок: {len(tickets)}</b>")
        
        for t in tickets:
            t_id, name, dept, issue = t
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🆗 Взять в работу", callback_data=f"adm_work_{t_id}"))
            
            text = (f"🆔 <b>Заявка №{t_id}</b>\n"
                    f"👤 Клиент: {name}\n"
                    f"📂 Отдел: {dept}\n"
                    f"📝 Суть: {issue}")
            bot.send_message(message.chat.id, text, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('adm_work_'))
    def handle_admin_take(call):
        ticket_id = call.data.split("_")[2]
        logic.update_ticket_status(ticket_id, "IN_PROGRESS")
        
        new_text = call.message.text + f"\n\n👨‍💻 <b>Взял в работу:</b> {call.from_user.first_name}"
        bot.edit_message_text(new_text, call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.answer_callback_query(call.id, "Заявка закреплена")