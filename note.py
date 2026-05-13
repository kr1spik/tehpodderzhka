from telebot import types
from config import ADMIN_IDS

def send_new_ticket_notification(bot, ticket_id, user_name, dept, issue):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🆗 Взять в работу", callback_data=f"adm_work_{ticket_id}"))
    
    text = (
        f"🔔 <b>НОВАЯ ЗАЯВКА №{ticket_id}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"👤 <b>Клиент:</b> {user_name}\n"
        f"📂 <b>Отдел:</b> {dept}\n"
        f"📝 <b>Суть:</b> {issue}"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, text, reply_markup=markup, parse_mode="HTML")
        except Exception as e:
            print(f"Не удалось отправить уведомление админу {admin_id}: {e}")