from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from app.db import query_db  # שימוש בפונקציות הקיימות שלך
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# מיפוי פעולות לפי role_id
ROLE_ACTIONS = {
    1: ["ניהול משתמשים", "צפייה בכל המידע", "עריכת נתונים"],
    2: ["צפייה בדוחות", "אישור בקשות"],
    3: ["ניהול הזמנות"],
    4: ["צפייה בנתונים בלבד"],
}

# רשימת הטבלאות הזמינות לתחקור
ADMIN_TABLES = ["dev_tg_users", "dev_employees", "dev_roles", "dev_customers"]

# פונקציה להצגת פעולות למשתמש
async def user_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    # קבלת role_id מהמסד
    query = "SELECT role_id FROM dev_tg_users WHERE telegram_id = :telegram_id"
    params = {"telegram_id": telegram_id}
    result = query_db(query, params, fetchone=True)
    role_id = result["role_id"] if result else None

    if not role_id:
        await update.message.reply_text(
            "אינך מזוהה במערכת. אנא הירשם או פנה למנהל."
        )
        return

    # קבלת הפעולות לפי ה-role_id
    actions = ROLE_ACTIONS.get(role_id, [])
    if not actions:
        await update.message.reply_text(
            "אין לך הרשאות לביצוע פעולות."
        )
        return

    # יצירת כפתורים לפי הפעולות
    buttons = [
        [InlineKeyboardButton(action, callback_data=f"action_{action}")]
        for action in actions
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "בחר פעולה מהרשימה:",
        reply_markup=reply_markup
    )

# פונקציה לניהול משתמשים
async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(table, callback_data=f"table_{table}")]
        for table in ADMIN_TABLES
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.callback_query.edit_message_text(
        text="בחר טבלה לתחקור:",
        reply_markup=reply_markup
    )

# פונקציה להצגת עמודות הטבלה
async def show_table_columns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    table_name = query.data[6:]
    context.user_data["selected_table"] = table_name

    # שאילתה לשמות העמודות
    try:
        sql_query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = :table_name
        """
        params = {"table_name": table_name}
        results = query_db(sql_query, params)

        if not results:
            await query.edit_message_text(
                text=f"לא נמצאו עמודות בטבלה '{table_name}'."
            )
            return

        columns = [row["column_name"] for row in results]
        columns_text = "\n".join(columns)

        # הצגת רשימת העמודות ושאלה על פילטר
        buttons = [
            [
                InlineKeyboardButton("כן, הוסף פילטר", callback_data="filter_yes"),
                InlineKeyboardButton("לא, המשך ללא פילטר", callback_data="filter_no")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await query.edit_message_text(
            text=f"עמודות בטבלה '{table_name}':\n{columns_text}\n\nהאם תרצה להוסיף פילטר?",
            reply_markup=reply_markup
        )
    except Exception as e:
        await query.edit_message_text(
            text=f"אירעה שגיאה בהצגת עמודות הטבלה: {e}"
        )

# פונקציה לביצוע השאילתה
async def execute_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    table_name = context.user_data.get("selected_table")
    if not table_name:
        await query.edit_message_text("אירעה שגיאה: הטבלה לא נבחרה.")
        return

    if query.data == "filter_no":
        # שאילתה ללא פילטר
        sql_query = f"SELECT * FROM {table_name} LIMIT 10"
        results = query_db(sql_query)
    elif query.data == "filter_yes":
        # בקשת תנאי WHERE
        logger.info("Setting awaiting_filter to True")

        await query.edit_message_text(
            text=f"הכנס תנאי `WHERE` עבור הטבלה '{table_name}' (לדוגמה: age > 30 או name = 'John'):"
        )
        context.user_data["awaiting_filter"] = True
        return

    if results:
        result_text = "\n".join([str(row) for row in results])
        await query.edit_message_text(
            text=f"תוצאות מתוך הטבלה '{table_name}':\n\n{result_text}"
        )
    else:
        await query.edit_message_text(
            text=f"לא נמצאו תוצאות בטבלה '{table_name}'."
        )

# פונקציה לטיפול בתנאי WHERE
async def handle_filter_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Handling filter input...")
    logger.info(f"context.user_data: {context.user_data}")
    if not context.user_data.get("awaiting_filter"):
        return

    table_name = context.user_data.get("selected_table")
    if not table_name:
        await update.message.reply_text("אירעה שגיאה: הטבלה לא נבחרה.")
        return

    where_condition = update.message.text.strip()

    try:
        sql_query = f"SELECT * FROM {table_name} WHERE {where_condition} LIMIT 10"
        results = query_db(sql_query)

        if results:
            result_text = "\n".join([str(row) for row in results])
            await update.message.reply_text(
                text=f"תוצאות מתוך הטבלה '{table_name}' עם הפילטר:\n\n{result_text}"
            )
        else:
            await update.message.reply_text(
                text=f"לא נמצאו תוצאות בטבלה '{table_name}' עבור הפילטר."
            )
    except Exception as e:
        await update.message.reply_text(
            text=f"אירעה שגיאה בביצוע השאילתה: {e}"
        )
    finally:
        context.user_data["awaiting_filter"] = False
