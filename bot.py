import os
import re
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
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

# Helper functions
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    admins = await context.bot.get_chat_administrators(chat.id)
    return any(admin.user.id == user.id for admin in admins)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Hello! I'm your group help bot.")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.new_chat_members:
            return

        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                continue

            name = member.full_name
            username = f"@{member.username}" if member.username else "(no username)"
            user_id = member.id

            welcome_message = (
                f"မင်္ဂလာပါ {name}\n"
                f"Username - {username} ({user_id})\n\n"
                f"Voice Of Mandalay (VOM) တော်လှန်ရေးသတင်း Group မှကြိုဆိုပါတယ်။\n\n"
                f"Voice Of Mandalay (VOM) တော်လှန်ရေးသတင်း Group မှကြိုဆိုပါတယ်။\n\n"
                f"ကျွန်တော်ကတော့ စကစကိုတော်လှန်နေတဲ့တော်လှန်‌ရေးမှာပါဝင်နေတဲ့ တော်လှန်စက်ရုပ်ဖြစ်ပါတယ်။\n"
                f"ကျွန်တော်တို့ Voice Of Mandalay (VOM) Group အတွင်းဝင်ရောက်လာမည်ဆိုပါက "
                f"မိဘပြည်သူများ၏ လုံခြုံရေးအတွက် အောက်ပါအချက်များကို သတိပြုရန် လိုအပ်ပါသည်။\n\n"
                f"၁။ Profile တွင် မိမိ၏ပုံအစစ်မှန်ကို မတင်ထားရန်။\n"
                f"၂။ ဖုန်းနံပါတ်ကို ဖျောက်ထားရန်။\n"
                f"၃။ မိမိ၏တည်နေရာကို public chat သို့မဟုတ် DM တွင် မဖော်ပြရန်။"
                f"၄။ သတင်းပေးပို့လိုပါက admin ထံသို့ DM မှတစ်ဆင့် ဆက်သွယ်သတင်းပေးရန်။\n\n"
                f"မိဘပြည်သူများအနေဖြင့် -\n"
                f"• စကစ၏ ယုတ်မာရက်စက်မှုများ\n"
                f"• ဧည့်စားရင်းစစ်သတင်းများ\n"
                f"• စကစ၏ လှုပ်ရှားမှုသတင်းများ\n"
                f"• စစ်မှုထမ်းရန်ဖမ်းဆီးခေါ်ဆောင်မှုများ\n"
                f"တို့ကို သတင်းပေးချင်ပါက ⤵️\n"
                f"/admin ကိုနှိပ်ပြီး သတင်းပေးပါ။"
            )

      
            await update.message.reply_text(welcome_message)

    except Exception as e:
        logger.error(f"Welcome error: {e}")

async def filter_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    blocked_patterns = [r'http[s]?://', r'www\.', r'\.com', r't\.me/', r'@\w+']

    if any(re.search(pattern, text) for pattern in blocked_patterns):
        try:
            await update.message.delete()
            warning_msg = await context.bot.send_message(
                chat_id=update.message.chat.id,
                text=f⚠️ {update.message.from_user.mention_html()}, 🚫 Group အတွင်း Link ပေးပို့ခြင်းကိုတားမြစ်ထားသည်။",
                parse_mode=ParseMode.HTML
            )
            await warning_msg.delete(delay=10)
        except Exception as e:
            logger.error(f"Error in filter_links: {e}")

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules_text = """📜 <b>အုပ်စုစည်းမျဉ်းများ</b>:
1. လောင်းကစားကြော်ငြာများ၊ refer မပြုလုပ်ပါနဲ့။
2. တော်လှန်ရေးနှင့်ပတ်သတ်သောအကြောင်းအရာများကို လွတ်လပ်စွာ ဆွေးနွေးနိုင်ပါသည်။
3. မိဘပြည်သူများကို စိတ်အနှောက်အယှက်ဖြစ်စေသော message များ မပို့ရ။
4. တော်လှန်ပြည်သူအချင်းချင်း စိတ်ဝမ်းကွဲစေနိုင်သော စကားများ မပြောရ။

<b>မှတ်ချက်</b>:
အခြားစည်းကမ်းချက်များ လိုအပ်လာပါက admin များမှ ထပ်မံ သတ်မှတ်သွားပါမည်။
"""

    await update.message.reply_text(rules_text, parse_mode=ParseMode.HTML)

async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    predefined_admins = ["@Oakgyi1116", "@bebeex124", "@GuGuLay1234"]
    message = (
        "🔷 <b>Admin များ:</b>\n\n" +
        "\n".join([f"• {admin}" for admin in predefined_admins]) +
        "\n\nသတင်းပေးရန် ဖော်ပြထားသော admin DM ထံသို့ ဆက်သွယ်ပါ။"
    )
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ သင့်အနေနဲ့ admin ဖြစ်ရပါမည်။")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("အသုံးပြုနည်း: /ban <user_id> [အကြောင်းရင်း]")
        return

    user_id = int(context.args[0])
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "စည်းမျဉ်းချိုးမှု"

    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text(f"🚫 User {user_id} ကို Ban လုပ်ပြီးပါပြီ။\nအကြောင်းရင်း: {reason}")
    except Exception as e:
        logger.error(f"Ban error: {e}")
        await update.message.reply_text("❌ Ban လုပ်ရာတွင် အမှားတစ်ခုဖြစ်နေသည်။")

async def report_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        reported_msg = update.message.reply_to_message
        if not reported_msg:
            await update.message.reply_text("⚠️ Reply ပြန်ပြီးမှ /report သုံးပါ။")
            return

        reporter = update.effective_user
        reported_user = reported_msg.from_user

        report_text = (
            f"⚠️ Report\n"
            f"👤 Reported by: {reporter.mention_html()} ({reporter.id})\n"
            f"🧾 Target: {reported_user.mention_html()} ({reported_user.id})\n\n"
            f"📄 Message:\n{reported_msg.text or 'Media'}"
        )

        admins = await context.bot.get_chat_administrators(update.effective_chat.id)
        for admin in admins:
            try:
                await context.bot.send_message(chat_id=admin.user.id, text=report_text, parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.error(f"Report send error: {e}")
    except Exception as e:
        logger.error(f"Report error: {e}")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set")

    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rules", rules))
    application.add_handler(CommandHandler("admin", admin_list))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("report", report_user))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), filter_links))

    logger.info("🤖 Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
