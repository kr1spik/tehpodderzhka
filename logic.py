import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('support.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            department TEXT,
            issue TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'NEW'
        )
    ''')
    conn.commit()
    conn.close()

def save_ticket(user_id, username, first_name, department, issue):
    try:
        conn = sqlite3.connect('support.db')
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            '''INSERT INTO tickets (user_id, username, first_name, department, issue, created_at) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, username, first_name, department, issue, now)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False
    
def update_ticket_status(ticket_id, new_status):
    conn = sqlite3.connect('support.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE tickets SET status = ? WHERE id = ?', (new_status, ticket_id))
    conn.commit()
    conn.close()

def get_ticket_info(ticket_id):
    conn = sqlite3.connect('support.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, department, issue FROM tickets WHERE id = ?', (ticket_id,))
    data = cursor.fetchone()
    conn.close()
    return data

FAQ = {
    "доставка": (
        "🚚 <b>Информация о доставке:</b>\n\n"
        "1. <b>Курьерская доставка:</b> Осуществляется в течение 1-2 рабочих дней. Стоимость — 350₽ (бесплатно при заказе от 5000₽).\n"
        "2. <b>Пункты выдачи (СДЭК/Boxberry):</b> Срок доставки 3-5 дней. Вы можете выбрать удобный пункт при оформлении.\n"
        "3. <b>Почта России:</b> Отправка в любой регион. Сроки зависят от удаленности."
    ),
    "оплата": (
        "💳 <b>Способы оплаты:</b>\n\n"
        "• Банковские карты (Visa, MasterCard, МИР) онлайн на сайте.\n"
        "• Система быстрых платежей (СБП).\n"
        "• Сервис 'Долями' (оплата частями без процентов).\n"
        "• Наличными или картой при получении (доступно для курьерской доставки)."
    ),
    "возврат": (
        "🔄 <b>Правила возврата и обмена:</b>\n\n"
        "Вы можете вернуть товар надлежащего качества в течение <b>14 дней</b>, если:\n"
        "• Сохранен товарный вид и все бирки.\n"
        "• Товар не был в употреблении.\n"
        "• Есть чек или подтверждение оплаты.\n\n"
        "<i>Для оформления возврата напишите нам в отдел продаж через кнопку 'Поддержка'.</i>"
    ),
    "статус заказа": (
        "📦 <b>Как узнать, где мой заказ?</b>\n\n"
        "После оформления вам приходит SMS и письмо на почту с трек-номером. "
        "Проверить текущий статус можно на нашем сайте в разделе 'Мои заказы' "
        "или в приложении службы доставки по вашему номеру телефона."
    ),
    "скидки": (
        "🎁 <b>Акции и лояльность:</b>\n\n"
        "• <b>Первый заказ:</b> Используйте промокод 'HELLO' для скидки 10%.\n"
        "• <b>Бонусная программа:</b> Мы начисляем 5% кешбэка с каждой покупки на ваш личный счет.\n"
        "• <b>Распродажи:</b> Следите за разделом 'Sale' — там скидки доходят до 70%!"
    ),
    "контакты": (
        "📞 <b>Связь с нами:</b>\n\n"
        "• <b>Горячая линия:</b> 8-800-555-35-35 (Бесплатно по РФ).\n"
        "• <b>Email:</b> support@shopeverything.ru\n"
        "• <b>Режим работы:</b> Ежедневно с 09:00 до 21:00 по московскому времени.\n\n"
        "Также вы можете оставить заявку через этого бота, выбрав соответствующий отдел."
    ),
    "гарантия": (
        "🛡️ <b>Гарантийные обязательства:</b>\n\n"
        "На технически сложные товары (электронику) предоставляется официальная гарантия <b>12 месяцев</b>. "
        "В случае поломки мы бесплатно проведем экспертизу и ремонт. Сохраняйте гарантийный талон и электронный чек!"
    ),
    "опт": (
        "💼 <b>Оптовые закупки:</b>\n\n"
        "Мы всегда открыты к сотрудничеству с B2B партнерами. При заказе от 50 000₽ действуют спеццены. "
        "Пожалуйста, свяжитесь с <b>Отделом продаж</b> через поддержку для получения прайс-листа."
    )
}

def get_faq_answer(text):
    text = text.lower().strip()
    return FAQ.get(text)