from dotenv import load_dotenv
from handlers.start import start, test  # Import handlers
import os
from telegram.ext import Application, CommandHandler, Updater

load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Main function
def main():
    # Create the application
    print(BOT_TOKEN)
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test",test))
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()