from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === ВСТАВ СВІЙ ТОКЕН ===
BOT_TOKEN = "7811394855:AAGsvwF1ZTHn6SHHDjOM2DRc7pnrJPexe-Y"
OPERATOR_CHAT_ID = 1721787490  

# Відповіді на популярні питання
faq = {
    "як змінити пароль": "Щоб змінити пароль, зайдіть у налаштування профілю та оберіть 'Змінити пароль'.",
    "не можу увійти": "Спробуйте скинути пароль за допомогою функції 'Забув пароль'. Якщо не допоможе — напишіть нам.",
    "як зв'язатися з підтримкою": "Ви вже звернулись 😄 Ми на зв'язку!"
}

# Надіслати повідомлення оператору
async def send_message_to_operator(context: ContextTypes.DEFAULT_TYPE, name, message):
    text = f"📩 Нове питання від {name}:\n\n{message}"
    await context.bot.send_message(chat_id=OPERATOR_CHAT_ID, text=text)

# Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    name = update.effective_user.full_name

    for q in faq:
        if q in text:
            await update.message.reply_text(faq[q])
            return

    await update.message.reply_text("На жаль, я не знайшов відповідь. Передаю ваше запитання оператору...")
    await send_message_to_operator(context, name, update.message.text)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вітаю! Я бот техпідтримки. Напишіть своє питання.")

# Команда /id — щоб дізнатися свій chat_id
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ваш Chat ID: {update.effective_chat.id}")

# Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущено!")
    app.run_polling()
