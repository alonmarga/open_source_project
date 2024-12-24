# def start(update, context):
#     update.message.reply_text("Hello! I'm your Telegram bot!")


async def start(update, context):
    await update.message.reply_text("Hello! I'm your Telegram bot!")


async def test(update, context):
    await update.message.reply_text("test! I'm your test Telegram bot!")