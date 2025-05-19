from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = ""
GROUP_CHAT_ID = -1002544676823  

faq = {
    "як змінити пароль": "Щоб змінити пароль, зайдіть у налаштування профілю та оберіть 'Змінити пароль'.",
    "не можу увійти": "Спробуйте скинути пароль за допомогою функції 'Забув пароль'. Якщо не допоможе — напишіть нам.",
    "як зв'язатися з підтримкою": "Ви вже звернулись 😄 Ми на зв'язку!",
    "працюєте у вихідні?": "Так! Наша підтримка працює 7 днів на тиждень — ми завжди на зв’язку 💬",
    "розробник": "Бот створено 💖 Анастасією Оношко",
    "дякую, питання вирішено": (
        "Раді, що змогли допомогти!\n"
        "Дякуємо за звернення 💻\n"
        "Гарного дня! ✨\n\n"
        "by Анастасія Оношко"
    )
}






active_tickets = {}
thread_to_user = {}
user_replied = {} 

async def create_forum_topic(context: ContextTypes.DEFAULT_TYPE, user_full_name: str) -> int:
    result = await context.bot.create_forum_topic(
        chat_id=GROUP_CHAT_ID,
        name=f"Запит від {user_full_name}"
    )
    return result.message_thread_id


async def send_message_to_topic(context: ContextTypes.DEFAULT_TYPE, user_id, user_full_name, message):
    if user_id not in active_tickets:
        thread_id = await create_forum_topic(context, user_full_name)
        active_tickets[user_id] = thread_id
        thread_to_user[thread_id] = user_id
    else:
        thread_id = active_tickets[user_id]

    text = f"📩 Питання від {user_full_name}:\n\n{message}"

    try:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, message_thread_id=thread_id, text=text)
    except Exception as e:
        print(f"❌ Помилка при відправці повідомлення в тред: {e}")
        raise

    return thread_id


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user_id = update.effective_user.id
    name = update.effective_user.full_name

    for q in faq:
        if q in text:
            await update.message.reply_text(faq[q])
            return

    if user_id not in user_replied:
        await update.message.reply_text("На жаль, я не знайшов відповідь. Передаю ваше запитання оператору...")
        user_replied[user_id] = True  

    try:
        thread_id = await send_message_to_topic(context, user_id, name, update.message.text)
    except Exception as e:
        await update.message.reply_text("❌ Помилка при створенні треда. Спробуйте ще раз.")
        return

    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        message_thread_id=thread_id,
        text=""
    )


async def handle_group_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or not update.message.is_topic_message:
        return  

    thread_id = update.message.message_thread_id
    if thread_id not in thread_to_user:
        return

    user_id = thread_to_user[thread_id]
    text = update.message.text

    try:
        await context.bot.send_message(chat_id=user_id, text=f"💬 Відповідь оператора: \n \n{text}")
    except Exception as e:
        print(f"❌ Не вдалося надіслати відповідь користувачу {user_id}: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вітаю! Я бот техпідтримки. Напишіть своє питання 😁")


if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_reply))

    print("🤖 Бот запущено! Очікуємо на запитання... ❌ ")
    app.run_polling()
