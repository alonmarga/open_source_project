from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler
import os
import logging
from handlers.start import start, test,test2

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define FastAPI app
app = FastAPI()

# Initialize Telegram application
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set!")

application = Application.builder().token(BOT_TOKEN).build()

# Initialize the bot
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Telegram bot...")
    await application.initialize()  # חשוב לאתחל את הבוט בזמן הפעלת היישום



# Add bot command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("test", test))
application.add_handler(CommandHandler("test", test2))

# Webhook endpoint for Telegram
@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    return {"ok": True}
