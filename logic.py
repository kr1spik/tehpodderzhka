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
            department TEXT,
            issue TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'NEW'
        )
    ''')
    conn.commit()
    conn.close()

def save_ticket(user_id, username, department, issue):
    try:
        conn = sqlite3.connect('support.db')
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            'INSERT INTO tickets (user_id, username, department, issue, created_at) VALUES (?, ?, ?, ?, ?)',
            (user_id, username, department, issue, now)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

FAQ = {
    "привет": "Здравствуйте! Я помогу вам с заказом или свяжу со специалистом.",
    "как купить": "Добавьте товары в корзину, выберите способ доставки и оплатите заказ.",
    "статус заказа": "Введите номер заказа на нашем сайте в разделе 'Трекинг'.",
    "возврат": "Вернуть товар можно в течение 14 дней, если сохранены бирки и упаковка.",
    "гарантия": "На всю электронику действует гарантия 12 месяцев.",
    "доставка": "Мы доставляем курьером по городу или почтой по всей стране.",
    "оплата": "Мы принимаем карты, СБП и оплату при получении.",
    "скидки": "Все актуальные акции доступны в разделе 'Распродажа' на сайте."
}

def get_faq_answer(text):
    text = text.lower().strip()
    return FAQ.get(text)