import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Состояния для диалога
(
    NAME_PHONE, CITY, ADDRESS, TIME, COMMENT, PHOTO
) = range(6)

# Ваша TELEGRAM ID для получения заявок
ADMIN_CHAT_ID = 404748283

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я бот для заказа химчистки.\n\nНажми /order, чтобы оставить заявку.")


async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите имя и номер телефона (в одной строке):")
    return NAME_PHONE

async def name_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name_phone"] = update.message.text.strip()
    await update.message.reply_text("🏙 Укажите город:")
    return CITY

async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text.strip()
    await update.message.reply_text("📍 Адрес в формате: подъезд-этаж-квартира — код домофона")
    return ADDRESS

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text.strip()
    await update.message.reply_text("🕓 Удобное время (например: утром, вечером):")
    return TIME

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["time"] = update.message.text.strip()
    await update.message.reply_text("✏ Комментарий (тип мебели и пожелания):")
    return COMMENT

async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["comment"] = update.message.text.strip()
    await update.message.reply_text("📷 Прикрепите фото или нажмите /skip, чтобы пропустить.")
    return PHOTO

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    context.user_data["photo"] = photo
    await send_summary(update, context)
    return ConversationHandler.END

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["photo"] = None
    await send_summary(update, context)
    return ConversationHandler.END

async def send_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    text = f"""{d['name_phone']}
{d['city']}
{d['address']}
{d['time']}
{d['comment']}"""

    # Отправка админу
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)

    # Отправка фото если было
    if d.get("photo"):
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=d["photo"])

    await update.message.reply_text("✅ Спасибо! Ваша заявка отправлена.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Заявка отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    import config
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("order", order)],
        states={
            NAME_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_phone)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, time)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment)],
            PHOTO: [
                MessageHandler(filters.PHOTO, photo),
                CommandHandler("skip", skip_photo),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
