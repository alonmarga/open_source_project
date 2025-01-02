from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from app.db import query_db
import csv
from io import StringIO

# טבלאות שמותר לצפות בהן לפי role_id
VIEWABLE_TABLES = {
    1: ["dev_tg_users", "dev_employees", "dev_roles", "dev_customers"],  # כל הטבלאות
    3: ["dev_orders", "dev_products"],  # טבלאות מסוימות בלבד
    4: ["dev_reports"],  # לדוגמה
}

# פונקציה להצגת רשימת הטבלאות
async def view_tables(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    # בדיקת role_id מהמסד
    query = "SELECT role_id FROM dev_tg_users WHERE telegram_id = :telegram_id"
    params = {"telegram_id": telegram_id}
    result = query_db(query, params, fetchone=True)
    role_id = result["role_id"] if result else None

    if not role_id:
        await update.message.reply_text("אינך מזוהה במערכת. אנא הירשם או פנה למנהל.")
        return

    # הבאת הטבלאות שהמשתמש יכול לצפות בהן
    tables = VIEWABLE_TABLES.get(role_id, [])
    if not tables:
        await update.message.reply_text("אין לך הרשאות לצפייה בטבלאות.")
        return

    # יצירת כפתורים לצפייה בטבלאות
    buttons = [
        [InlineKeyboardButton(table, callback_data=f"view_table_{table}")]
        for table in tables
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text("בחר טבלה לצפייה:", reply_markup=reply_markup)


# פונקציה להצגת שאלה למשתמש על פורמט התוצאה
async def display_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    table_name = query.data.replace('view_table_', '')  # חילוץ שם הטבלה מה-callback_data
    context.user_data["selected_table"] = table_name  # שמירת שם הטבלה להמשך

    # הצגת אפשרויות פורמט למשתמש
    buttons = [
        [
            InlineKeyboardButton("פורמט רגיל", callback_data="format_plain"),
            InlineKeyboardButton("שליחת קובץ", callback_data="format_file"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(
        text=f"באיזה פורמט תרצה להציג את תוכן הטבלה '{table_name}'?",
        reply_markup=reply_markup
    )


# פונקציה להצגת התוצאה בפורמט הנבחר
async def display_table_in_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    table_name = context.user_data.get("selected_table")
    if not table_name:
        await query.edit_message_text("אירעה שגיאה: הטבלה לא נבחרה.")
        return

    sql_query = f"SELECT * FROM {table_name} LIMIT 10"
    try:
        results = query_db(sql_query)

        if not results:
            await query.edit_message_text(
                text=f"לא נמצאו נתונים בטבלה '{table_name}'."
            )
            return

        if query.data == "format_plain":
            # הצגת נתונים בפורמט רגיל
            rows = [" | ".join([f"{key}: {value}" for key, value in row.items()]) for row in results]
            result_text = "\n".join(rows)

            await query.edit_message_text(
                text=f"תוכן טבלה '{table_name}':\n\n{result_text}"
            )

        elif query.data == "format_file":
            # יצירת קובץ CSV ושליחתו
            csv_file = StringIO()
            writer = csv.DictWriter(csv_file, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

            csv_file.seek(0)
            await query.message.reply_document(
                document=csv_file,
                filename=f"{table_name}.csv",
                caption=f"קובץ הנתונים של הטבלה '{table_name}'"
            )
    except Exception as e:
        await query.edit_message_text(
            text=f"אירעה שגיאה בהצגת תוכן הטבלה '{table_name}': {e}"
        )
