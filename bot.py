import os
import telebot
from telebot import types

# Токен и твой ID лучше задавать через переменные окружения (Secrets)
BOT_TOKEN = os.getenv("BOT_TOKEN", "ВСТАВЬ_СЮДА_ТОКЕН_ОТ_BOTFATHER")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))  # Замени на свой Telegram ID

bot = telebot.TeleBot(BOT_TOKEN)

# Временное хранилище шагов пользователя
user_data = {}


@bot.message_handler(commands=["start"])
def cmd_start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Оставить заявку"))

    bot.send_message(
        chat_id,
        "Привет! Это бот **PulseDesk**.\n"
        "Я помогу быстро передать вашу задачу менеджеру.\n\n"
        "Нажмите кнопку ниже, чтобы начать:",
        parse_mode="Markdown",
        reply_markup=markup,
    )


@bot.message_handler(func=lambda msg: msg.text == "Оставить заявку")
def ask_name(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    msg = bot.send_message(
        chat_id,
        "Шаг 1/3. Как к вам обращаться?",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    bot.register_next_step_handler(msg, process_name)


def process_name(message):
    chat_id = message.chat.id
    user_data[chat_id]["name"] = message.text.strip()

    msg = bot.send_message(chat_id, "Шаг 2/3. Опишите кратко вашу задачу или вопрос:")
    bot.register_next_step_handler(msg, process_task)


def process_task(message):
    chat_id = message.chat.id
    user_data[chat_id]["task"] = message.text.strip()

    msg = bot.send_message(
        chat_id,
        "Шаг 3/3. Оставьте контакт для связи (телефон, @username или email):",
    )
    bot.register_next_step_handler(msg, process_contact)


def process_contact(message):
    chat_id = message.chat.id
    user_data[chat_id]["contact"] = message.text.strip()

    data = user_data[chat_id]
    tg_user = f"@{message.from_user.username}" if message.from_user.username else "скрыт"

    # Формируем карточку заявки для тебя (админа)
    admin_text = (
        "📥 **Новая заявка из PulseDesk**\n\n"
        f"👤 **Имя:** {data['name']}\n"
        f"📝 **Задача:** {data['task']}\n"
        f"📞 **Контакт:** {data['contact']}\n"
        f"🔗 **Профиль TG:** {tg_user} (ID: `{chat_id}`)"
    )

    bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")

    # Возвращаем кнопку пользователю
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Оставить заявку"))

    bot.send_message(
        chat_id,
        "✅ Заявка принята! Скоро свяжемся с вами.",
        reply_markup=markup,
    )
    user_data.pop(chat_id, None)


if __name__ == "__main__":
    print("LeadPulse запущен...")
    bot.infinity_polling()