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
from handlers.views import view_tables, display_table, display_table_in_format
from handlers.edit import edit_tables, select_action, perform_action, handle_input
from handlers.general import show_help

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

application.add_handler(CommandHandler("help", show_help))

application.add_handler(CommandHandler("log_in", check_or_register_user))
# קליטת לחיצות על כפתורים (כן רוצה/לא רוצה להירשם + אישור/דחייה אדמין)
application.add_handler(CallbackQueryHandler(handle_button_click, pattern="register_yes|register_no"))
application.add_handler(CallbackQueryHandler(handle_admin_approval, pattern="approve_|deny_"))
# קודם המשתמש
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_registration_details), group=0)
# אחר כך האדמין
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_code_submission), group=1)

application.add_handler(CommandHandler("view", view_tables))
application.add_handler(CallbackQueryHandler(display_table, pattern="^view_table_"))
application.add_handler(CallbackQueryHandler(display_table_in_format, pattern="^format_"))

application.add_handler(CommandHandler("edit", edit_tables))
application.add_handler(CallbackQueryHandler(select_action, pattern="^edit_table_"))
application.add_handler(CallbackQueryHandler(perform_action, pattern="^action_"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
application.add_handler(CallbackQueryHandler(edit_tables, pattern="^back_to_tables$"))



@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    return {"ok": True}
