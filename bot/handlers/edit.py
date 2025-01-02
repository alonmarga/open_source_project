from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from app.db import query_db

# טבלאות ופעולות שמותר לערוך לפי role_id
EDITABLE_TABLES = {
    1: {  # דרגת מנהל
        "dev_tg_users": ["insert", "update", "delete"],
        "dev_employees": ["update"],
    },
    3: {  # דרגת עובד רגיל
        "dev_orders": ["insert", "update"],
    },
}

# פונקציה להצגת רשימת הטבלאות לעריכה
async def edit_tables(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_query = update.callback_query if update.callback_query else None
    if callback_query:
        await callback_query.answer()

    telegram_id = update.effective_user.id

    # בדיקת role_id מהמסד
    sql_query = "SELECT role_id FROM dev_tg_users WHERE telegram_id = :telegram_id"
    params = {"telegram_id": telegram_id}
    result = query_db(sql_query, params, fetchone=True)
    role_id = result["role_id"] if result else None

    if not role_id:
        await update.message.reply_text("אינך מזוהה במערכת. אנא הירשם או פנה למנהל.")
        return

    # הבאת הטבלאות שהמשתמש יכול לערוך
    tables = EDITABLE_TABLES.get(role_id, {})
    if not tables:
        await update.message.reply_text("אין לך הרשאות לעריכת טבלאות.")
        return

    # יצירת כפתורים לטבלאות
    buttons = [
        [InlineKeyboardButton(table, callback_data=f"edit_table_{table}")]
        for table in tables.keys()
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    if callback_query:
        # אם הקריאה היא מ-CallbackQuery
        await callback_query.edit_message_text("בחר טבלה לעריכה:", reply_markup=reply_markup)
    else:
        # אם הקריאה היא מפקודה
        await update.message.reply_text("בחר טבלה לעריכה:", reply_markup=reply_markup)



# פונקציה להצגת הפעולות האפשריות על הטבלה
async def select_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    table_name = query.data.replace('edit_table_', '')  # חילוץ שם הטבלה
    context.user_data["selected_table"] = table_name  # שמירת שם הטבלה להמשך

    # הבאת הפעולות שמותרות לטבלה
    telegram_id = update.effective_user.id
    query_role = "SELECT role_id FROM dev_tg_users WHERE telegram_id = :telegram_id"
    role_result = query_db(query_role, {"telegram_id": telegram_id}, fetchone=True)
    role_id = role_result["role_id"] if role_result else None
    actions = EDITABLE_TABLES.get(role_id, {}).get(table_name, [])

    if not actions:
        await query.edit_message_text("אין לך הרשאות לערוך את הטבלה שנבחרה.")
        return

    # יצירת כפתורים לפעולות
    buttons = [
        [InlineKeyboardButton(action.capitalize(), callback_data=f"action_{action}")]
        for action in actions
    ]
    buttons.append([InlineKeyboardButton("⬅️ אחורה", callback_data="back_to_tables")])
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(
        text=f"בחר פעולה לטבלה '{table_name}':", reply_markup=reply_markup
    )


# פונקציה לביצוע פעולה על הטבלה
async def perform_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data.replace('action_', '')  # חילוץ שם הפעולה
    table_name = context.user_data.get("selected_table")

    if not table_name:
        await query.edit_message_text("אירעה שגיאה: הטבלה לא נבחרה.")
        return

    context.user_data["selected_action"] = action

    if action == "insert":
        await query.edit_message_text(
            text=f"הכנס את הנתונים להוספה בטבלה '{table_name}' בפורמט: `key1=value1, key2=value2`",
            parse_mode="Markdown"
        )
    elif action == "update":
        await query.edit_message_text(
            text=f"הכנס מזהה (`id`) ונתונים לעדכון בטבלה '{table_name}' בפורמט: `id=1, key1=value1, key2=value2`",
            parse_mode="Markdown"
        )
    elif action == "delete":
        await query.edit_message_text(
            text=f"הכנס מזהה (`id`) למחיקה בטבלה '{table_name}' בפורמט: `id=1`",
            parse_mode="Markdown"
        )


# פונקציה לטיפול בקלט מהמשתמש וביצוע הפעולה
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    table_name = context.user_data.get("selected_table")
    action = context.user_data.get("selected_action")
    input_text = update.message.text.strip()

    if not table_name or not action:
        await update.message.reply_text("אירעה שגיאה: לא נבחרה טבלה או פעולה.")
        return

    # עיבוד הקלט בהתאם לפעולה
    try:
        data = {key.strip(): value.strip() for key, value in (item.split('=') for item in input_text.split(','))}

        if action == "insert":
            query = f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({', '.join([f':{k}' for k in data.keys()])})"
        elif action == "update":
            if "id" not in data:
                raise ValueError("יש לספק מזהה `id` לעדכון.")
            id_value = data.pop("id")
            set_clause = ", ".join([f"{key} = :{key}" for key in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = :id"
            data["id"] = id_value
        elif action == "delete":
            if "id" not in data:
                raise ValueError("יש לספק מזהה `id` למחיקה.")
            query = f"DELETE FROM {table_name} WHERE id = :id"

        # ביצוע השאילתה
        query_db(query, data)
        await update.message.reply_text(f"הפעולה '{action}' בוצעה בהצלחה על הטבלה '{table_name}'.")
    except Exception as e:
        await update.message.reply_text(f"אירעה שגיאה: {e}")
