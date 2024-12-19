from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from app.db import query  # Import from the existing app.db module
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


def fetch_data(update: Update, context: CallbackContext):
    """
    Fetch data from the users table using app.db.query.
    """
    sql = "SELECT * FROM users;"
    try:
        data = query(sql)
        if not data:
            update.message.reply_text("No users found.")
            return

        response = "\n".join([f"ID: {row['id']}, Username: {row['username']}" for row in data])
        update.message.reply_text(f"Users:\n{response}")
    except Exception as e:
        update.message.reply_text(f"Error querying the database: {e}")


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Use /fetch to query data from the database.")


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set.")

    updater = Updater(BOT_TOKEN)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("fetch", fetch_data))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
