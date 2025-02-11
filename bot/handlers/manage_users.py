import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from app.db import query_db, insert_db, update_db  # וודא שיש לך פונקציות אלו ב-db.py
import os
import secrets


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# מילון לשמירת בקשות רישום זמניות (לפי user_id)
pending_requests = {}
# מילון לשמירת בקשות לאישור מצד האדמין (לפי admin_id)
admin_approvals = {}

async def check_or_register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_user.id

    # בדיקה אם המשתמש קיים בטבלה dev_tg_users
    sql_check_user = f"SELECT * FROM {os.environ.get('DB_DEV_TABLE_TG_USERS')} WHERE telegram_id = :telegram_id;"
    user_in_db = query_db(sql_check_user, parameters={"telegram_id": chat_id}, fetchone=True)

    if user_in_db:
        await update.message.reply_text("ברוך הבא בחזרה! המשתמש שלך מאומת במערכת.")
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("כן, אני רוצה להירשם", callback_data="register_yes")],
            [InlineKeyboardButton("לא, תודה", callback_data="register_no")]
        ])
        await update.message.reply_text(
            "לא מצאתי אותך במערכת. האם תרצה להירשם?",
            reply_markup=keyboard
        )

setattr(check_or_register_user, "desc", "רישום או בדיקת משתמש במערכת.")



async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_q = update.callback_query
    await callback_q.answer()  # תשובה ללחיצה למניעת "loading"

    chat_id = callback_q.from_user.id
    if callback_q.data == "register_yes":
        # התחלת תהליך רישום
        pending_requests[chat_id] = {"step": "collect_details"}
        await callback_q.edit_message_text(
            "בבקשה כתוב את שמך הפרטי ושם המשפחה בפורמט הבא:\n\n`שם פרטי שם משפחה`",
            parse_mode="Markdown"
        )
    elif callback_q.data == "register_no":
        # ביטול רישום
        await callback_q.edit_message_text("אין בעיה, אולי בפעם אחרת.")


async def handle_registration_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ מקבל טקסט מהמשתמש; אם הוא בתהליך 'collect_details', מוסיף את העובד לטבלה ומודיע לאדמין. """
    logger.info(f"Entered handle_registration_details: from_user={update.message.from_user.id}, text={update.message.text}")
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    # אם אין בקשה פעילה או שהשלב אינו "collect_details" – נחזיר None כדי שההודעה תעבור הלאה
    if user_id not in pending_requests or pending_requests[user_id].get("step") != "collect_details":
        logger.info("Not in pending_requests or step != collect_details -> pass to next handler.")
        return None

    # נסה לפצל את השמות
    try:
        first_name, last_name = text.split(" ", 1)
    except ValueError:
        await update.message.reply_text(
            "יש להזין שם פרטי ושם משפחה בפורמט הבא:\n\n`שם פרטי שם משפחה`",
            parse_mode="Markdown"
        )
        return

    # הוספת שם פרטי ומשפחה לטבלת dev_employees
    sql_insert_emp = f"""
        INSERT INTO {os.environ.get('DB_DEV_TABLE_EMPLOYEES')} (emp_first_name, emp_last_name)
        VALUES (:emp_first_name, :emp_last_name)
        RETURNING emp_id;
    """
    result = insert_db(
        sql_insert_emp,
        parameters={"emp_first_name": first_name, "emp_last_name": last_name},
        returning=True
    )
    emp_id = result["emp_id"]

    # שמירת מצב זמני
    pending_requests[user_id].update({
        "emp_first_name": first_name,
        "emp_last_name": last_name,
        "emp_id": emp_id
    })

    # שליחת בקשה לאדמין (נניח שיש אדמין אחד, role_id=1)
    sql_get_admin = f"""SELECT telegram_id 
                        FROM {os.environ.get('DB_DEV_TABLE_TG_USERS')} 
                        WHERE role_id = 1 LIMIT 1;"""
    admin = query_db(sql_get_admin, fetchone=True)

    if admin:
        admin_id = admin["telegram_id"]
        # שולחים לאדמין כפתורים לאישור/דחייה
        await context.bot.send_message(
            chat_id=admin_id,
            text=(
                f"משתמש {user_id} מבקש להירשם:\n"
                f"שם פרטי: {first_name}\n"
                f"שם משפחה: {last_name}\n"
                f"האם לאשר? עליך ללחוץ 'אישור' או 'דחייה', ולאחר מכן להזין קוד תפקיד (ספרה)."
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("אישור", callback_data=f"approve_{user_id}"),
                    InlineKeyboardButton("דחייה", callback_data=f"deny_{user_id}")
                ]
            ])
        )

    await update.message.reply_text("הבקשה נשלחה לאישור. תקבל תשובה בקרוב.")


async def handle_admin_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ מטפל בלחיצה על הכפתור אישור/דחייה מצד האדמין. """
    callback_q = update.callback_query
    admin_id = callback_q.from_user.id
    data = callback_q.data

    logger.info(f"handle_admin_approval: from_user={admin_id}, data={data}")

    await callback_q.answer()

    # user_id זה ה-ID של המשתמש שמבקש להירשם
    user_id = int(data.split("_")[1])

    # בודקים אם יש בכלל בקשת רישום מצד המשתמש הזה
    if user_id not in pending_requests:
        await callback_q.edit_message_text("לא נמצאה בקשה פעילה לאישור/דחייה.")
        return

    if data.startswith("approve_"):
        user_data = pending_requests[user_id]
        admin_approvals[admin_id] = {
            "request_user_id": user_id,
            "emp_id": user_data["emp_id"]
        }
        # מחיקה מהמילון של המשתמש, כי כעת זה בטיפול אדמין
        pending_requests.pop(user_id, None)

        await callback_q.edit_message_text("אנא הזן את קוד התפקיד (ספרה) בהודעת טקסט.")
    elif data.startswith("deny_"):
        pending_requests.pop(user_id, None)
        await callback_q.edit_message_text(f"הבקשה נדחתה. משתמש {user_id} לא יכול להירשם.")
        await context.bot.send_message(chat_id=user_id, text="בקשתך נדחתה.")


async def handle_admin_code_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ מקבל טקסט מהאדמין שאישר את המשתמש ומזין קוד תפקיד. """
    logger.info(f"**Entering handle_admin_code_submission** with message: {update.message.text}")

    admin_id = update.message.from_user.id
    text = update.message.text.strip()

    # אם לא קיים מילון עבור ה-admin הזה – אין למי לאשר
    if admin_id not in admin_approvals:
        logger.info(f"admin_id {admin_id} not in admin_approvals -> pass to next handler")
        return None

    # שליפת הפרטים הרלוונטיים
    approval_data = admin_approvals.pop(admin_id)
    request_user_id = approval_data["request_user_id"]
    emp_id = approval_data["emp_id"]

    # בדיקת קוד תפקיד
    if not text.isdigit():
        # אם לא ספרה, החזר למילון ונבקש שוב
        admin_approvals[admin_id] = approval_data
        await update.message.reply_text("הקוד חייב להיות ספרה. אנא נסה שוב.")
        return

    role_id = int(text)
    access_token = secrets.token_urlsafe(32)
    # הכנסת המשתמש לטבלת dev_tg_users
    sql_insert_user = f"""
        INSERT INTO {os.environ.get('DB_DEV_TABLE_TG_USERS')} (telegram_id, role_id,access_token, created_at)
        VALUES (:telegram_id, :role_id, :access_token, NOW())
        RETURNING id;
    """
    insert_result = insert_db(
        sql_insert_user,
        parameters={
            "telegram_id": request_user_id,
            "role_id": role_id,
            "access_token":access_token
        },
        returning=True
    )
    tg_user_id = insert_result["id"]

    # עדכון טבלת dev_employees עם tg_id
    sql_update_emp = f"""
        UPDATE {os.environ.get('DB_DEV_TABLE_EMPLOYEES')}
        SET tg_id = :tg_id
        WHERE emp_id = :emp_id;
    """
    rows_updated = update_db(
        sql_update_emp,
        parameters={
            "tg_id": tg_user_id,
            "emp_id": emp_id
        }
    )

    if rows_updated > 0:
        await update.message.reply_text("המשתמש עודכן בהצלחה! ✅")
        # שולחים למשתמש הודעה שהוא אושר
        await context.bot.send_message(
            chat_id=request_user_id,
            text=f"בקשתך אושרה! קוד התפקיד שלך הוא: {role_id}"
        )
    else:
        await update.message.reply_text("שגיאה: לא עודכנו שורות בטבלת העובדים.")
