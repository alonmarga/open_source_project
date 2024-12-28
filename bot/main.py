from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
)
import os
import logging

# מייבאים מהקובץ manage_users את הפונקציות
from handlers.manage_users import (
    check_or_register_user,
    handle_button_click,
    handle_registration_details,
    handle_admin_approval,
    handle_admin_code_submission
)

# דוגמאות לפונקציות אחרות
from handlers.start import start, test, test2

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = FastAPI()

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set!")

application = Application.builder().token(BOT_TOKEN).build()

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Telegram bot...")
    await application.initialize()

# פקודות (לדוגמה)
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("test", test2))
application.add_handler(CommandHandler("check_user", check_or_register_user))

# קליטת לחיצות על כפתורים (כן רוצה/לא רוצה להירשם + אישור/דחייה אדמין)
application.add_handler(CallbackQueryHandler(handle_button_click, pattern="register_yes|register_no"))
application.add_handler(CallbackQueryHandler(handle_admin_approval, pattern="approve_|deny_"))

# קודם המשתמש
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_registration_details), group=0)
# אחר כך האדמין
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_code_submission), group=1)


@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    return {"ok": True}
