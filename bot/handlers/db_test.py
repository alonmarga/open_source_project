from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from app.db import query, insert  # פונקציה שמבצעת שאילתות

async def check_or_register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id

    # Check if the user exists in the database
    sql_check_user = "SELECT * FROM dev_tg_users WHERE telegram_id = :telegram_id;"
    user = query(sql_check_user, parameters={"telegram_id": chat_id}, fetchone=True)

    if user:  # If a user is found
        await update.message.reply_text("ברוך הבא בחזרה! המשתמש שלך מאומת במערכת.")
    else:
        # User not found, prompt for registration
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("כן, אני רוצה להירשם", callback_data="register_yes")],
            [InlineKeyboardButton("לא, תודה", callback_data="register_no")]
        ])
        await update.message.reply_text(
            "לא מצאתי אותך במערכת. האם תרצה להירשם?",
            reply_markup=keyboard
        )

# הנדלר לרישום
async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_query = update.callback_query  # Renamed variable to avoid conflict
    chat_id = callback_query.from_user.id

    if callback_query.data == "register_yes":
        # Insert the new user into the database
        sql_insert_user = """
        INSERT INTO dev_tg_users (telegram_id, created_at)
        VALUES (:telegram_id, NOW());
        """
        insert(sql_insert_user, parameters={"telegram_id": chat_id})
        await callback_query.answer("נרשמת בהצלחה!")
        await callback_query.edit_message_text("נרשמת בהצלחה למערכת!")
    elif callback_query.data == "register_no":
        await callback_query.answer("הבחירה התקבלה.")
        await callback_query.edit_message_text("אין בעיה, אולי בפעם אחרת.")