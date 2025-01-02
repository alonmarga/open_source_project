from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import logging
from app.db import query_db

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    הצגת רשימת הפקודות הזמינות למשתמשים רשומים בלבד.
    """
    # בדיקת אם המשתמש רשום במערכת
    chat_id = update.effective_user.id
    sql_check_user = "SELECT * FROM dev_tg_users WHERE telegram_id = :telegram_id;"
    user_in_db = query_db(sql_check_user, parameters={"telegram_id": chat_id}, fetchone=True)

    if not user_in_db:
        # אם המשתמש אינו רשום, הפנייה ל-login
        await update.message.reply_text(
            "נראה שאינך רשום במערכת. השתמש בפקודה /log_in כדי להירשם."
        )
        return

    # רשימת ה-CommandHandlers מתוך context.application.handlers
    handlers = context.application.handlers

    help_text = "ברוכים הבאים לבוט!\nהנה הפקודות הזמינות:\n\n"

    for priority, handler_list in handlers.items():
        for handler in handler_list:
            # מזהים רק CommandHandler
            if isinstance(handler, CommandHandler):
                commands = list(handler.commands)  # המרת frozenset לרשימה
                for command in commands:
                    callback = handler.callback  # הפונקציה המחוברת ל-CommandHandler
                    description = getattr(callback, "desc", "אין תיאור זמין.")  # שליפת `desc`
                    help_text += f"/{command} - {description}\n"

    help_text += "\nבבקשה השתמש בפקודות בהתאם להרשאות שלך. 😊"

    logger.info(help_text)  # לוג לבדיקת הפלט
    await update.message.reply_text(help_text)

setattr(show_help, "desc", "עזרה")
