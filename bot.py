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
    ContextTypes,
    ConversationHandler,
    filters,
)

# Состояния
(NAME_PHONE, CITY, ADDRESS, TIME, COMMENT, PHOTO) = range(6)

ADMIN_CHAT_ID = 404748283  # Твой Telegram ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Главное меню
main_menu = ReplyKeyboardMarkup([
    ["🧼 Заказать химчистку"],
    ["📸 Отправить фото", "💬 Связаться с оператором"],
    ["ℹ️ О нас", "📎 Прайс-лист"],
    ["❌ Отменить заявку"]
], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:", reply_markup=main_menu
    )

# Универсальная проверка на выход из диалога
def check_cancel_or_menu(text):
    return text in ["❌ Отменить заявку", "🧼 Заказать химчистку", "📸 Отправить фото",
                    "💬 Связаться с оператором", "ℹ️ О нас", "📎 Прайс-лист"]

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите имя и номер телефона:")
    return NAME_PHONE

async def name_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_cancel_or_menu(update.message.text):
        return await handle_menu_buttons(update, context)
    context.user_data["name_phone"] = update.message.text.strip()
    await update.message.reply_text("🏙 Укажите город:")
    return CITY

async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_cancel_or_menu(update.message.text):
        return await handle_menu_buttons(update, context)
    context.user_data["city"] = update.message.text.strip()
    await update.message.reply_text("📍 Адрес: подъезд-этаж-квартира — код домофона")
    return ADDRESS

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_cancel_or_menu(update.message.text):
        return await handle_menu_buttons(update, context)
    context.user_data["address"] = update.message.text.strip()
    await update.message.reply_text("🕓 Удобное время (например: утром, вечером):")
    return TIME

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_cancel_or_menu(update.message.text):
        return await handle_menu_buttons(update, context)
    context.user_data["time"] = update.message.text.strip()
    await update.message.reply_text("✏ Комментарий (тип мебели и пожелания):")
    return COMMENT

async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if check_cancel_or_menu(update.message.text):
        return await handle_menu_buttons(update, context)
    context.user_data["comment"] = update.message.text.strip()
    await update.message.reply_text("📷 Прикрепите фото или нажмите /skip, чтобы пропустить.")
    return PHOTO

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["photo"] = update.message.photo[-1].file_id
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
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
    if d.get("photo"):
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=d["photo"])
    await update.message.reply_text("✅ Спасибо! Ваша заявка отправлена.", reply_markup=main_menu)

async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "❌ Отменить заявку":
        await update.message.reply_text("Заявка отменена. Возвращаемся в главное меню.", reply_markup=main_menu)
        return ConversationHandler.END

    elif text == "🧼 Заказать химчистку":
        return await start_order(update, context)

    elif text == "📸 Отправить фото":
        await update.message.reply_text("📸 Пришлите фото загрязнённой мебели:")
        return PHOTO

    elif text == "💬 Связаться с оператором":
        await update.message.reply_text("📞 Напишите нам в Telegram: @White_Buddha
Или в WhatsApp: https://wa.me/qr/4HDE6MIQIIDVM1")

    elif text == "ℹ️ О нас":
        await update.message.reply_text("Мы занимаемся выездной химчисткой мебели и ковров в Москве и МО. Работаем качественно, быстро и по честной цене.")

    elif text == "📎 Прайс-лист":
        await update.message.reply_text("""🧾 Прайс:
- Диван от 1500₽
- Матрас от 1000₽
- Ковер от 500₽/м²""")

    else:
        await update.message.reply_text("Выберите действие из меню:", reply_markup=main_menu)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Заявка отменена.", reply_markup=main_menu)
    return ConversationHandler.END

def main():
    import config
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🧼 Заказать химчистку$"), start_order)],
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))

    app.run_polling()

if __name__ == "__main__":
    main()
