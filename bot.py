import os
import re
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters
)

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Hello! I'm your group help bot.")

# Admin checker
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    admins = await context.bot.get_chat_administrators(chat.id)
    return any(admin.user.id == user.id for admin in admins)

# Welcome message
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                continue
            name = member.full_name
            username = f"@{member.username}" if member.username else "(no username)"
            user_id = member.id
            welcome_message = (
                f"မင်္ဂလာပါ {name}\n"
                f"Username - {username} ({user_id})\n\n"
                f"Voice Of Mandalay (VOM) Group မှ ကြိုဆိုပါတယ်။\n\n"
                f"⚠️ သတိပြုရန်:\n"
                f"၁။ မိမိပုံအစစ်မတင်ပါနှင့်\n"
                f"၂။ ဖုန်းနံပါတ် ဖျောက်ထားပါ\n"
                f"၃။ တည်နေရာ မမျှဝေပါနှင့်\n"
                f"၄။ သတင်းပေးရန် admin ထံသို့ DM လုပ်ပါ။\n\n"
                f"သတင်းပေးရန် /admin ကိုနှိပ်ပါ။"
            )
            await update.message.reply_text(welcome_message)

# Filter Links
async def filter_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    blocked_patterns = [r"http[s]?://", r"www\.", r"\.com", r"t\.me/", r"@\w+"]
    if any(re.search(pattern, text) for pattern in blocked_patterns):
        try:
            await update.message.delete()
            warning = await context.bot.send_message(
                chat_id=update.message.chat.id,
                text=f"⚠️ {update.message.from_user.mention_html()} Group အတွင်း Link မတင်ပါနဲ့။",
                parse_mode=ParseMode.HTML
            )
            await asyncio.sleep(10)
            await warning.delete()
        except Exception as e:
            logger.error(f"Link filter error: {e}")

# Rules
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules_text = """
📜 <b>အုပ်စုစည်းမျဉ်းများ</b>:
1. လောင်းကစား/Refer များ တားမြစ်
2. တော်လှန်ရေးဆွေးနွေးမှုများ OK
3. Spam မဖြစ်အောင် ကြောင်းကြောင်းထည်ထည်
4. စကားလုံး ရိုသေမှုရှိစွာအသုံးပြုရန်
    """
    await update.message.reply_text(rules_text, parse_mode=ParseMode.HTML)

# Admins list
async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = ["@Oakgyi1116", "@bebeex124", "@GuGuLay1234"]
    msg = (
        "🔷 <b>Admin များ:</b>\n\n" +
        "\n".join([f"• {a}" for a in admins]) +
        "\n\nသတင်းပေးရန် DM လုပ်ပါ။"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# Ban command
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ သင့်မှာ admin 권한 မရှိပါ။")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("အသုံးပြုနည်း: /ban <user_id> [အကြောင်းအရင်း]")
        return

    user_id = int(context.args[0])
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "စည်းမျဉ်းချိုးမှု"

    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text(f"🚫 {user_id} ကို Ban လုပ်ခဲ့သည်။\nအကြောင်းအရင်း: {reason}")
    except Exception as e:
        logger.error(f"Ban Error: {e}")
        await update.message.reply_text("❌ Ban လုပ်ရာတွင် ပြဿနာရှိသည်။")

# Report command
async def report_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reported_msg = update.message.reply_to_message
    if not reported_msg:
        await update.message.reply_text("⚠️ Reply ပြန်ပြီးမှ /report ကိုသုံးပါ။")
        return

    reporter = update.effective_user
    reported_user = reported_msg.from_user
    report = (
        f"⚠️ <b>Report</b>\n"
        f"👤 By: {reporter.mention_html()} ({reporter.id})\n"
        f"🧾 Target: {reported_user.mention_html()} ({reported_user.id})\n"
        f"📄 Message:\n{reported_msg.text or 'Media'}"
    )

    admins = await context.bot.get_chat_administrators(update.effective_chat.id)
    for admin in admins:
        try:
            await context.bot.send_message(chat_id=admin.user.id, text=report, parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Sending report failed: {e}")

# ✅ Railway-compatible Main Function
async def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise Exception("Missing BOT_TOKEN in .env")

    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("admin", admin_list))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("report", report_user))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_links))

    print("🤖 Bot is starting...")
    await app.run_polling(close_loop=False)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
