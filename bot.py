import os
import re
import logging
from dotenv import load_dotenv
from telegram import Update, ChatPermissions
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from datetime import timedelta

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Warning Counter Store
user_warnings = {}

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
                f"ကျွန်တော်ကတော့ စကစကိုတော်လှန်နေတဲ့တော်လှန်‌ရေးမှာပါဝင်နေတဲ့ တော်လှန်စက်ရုပ် တစ်ကောင်ဖြစ်ပါတယ်။\n"
                f"ကျွန်တော်တို Voice Of Mandalay (VOM)တော်လှန်ရေးသတင်း Group အတွင်းဝင်ထားမည်ဆိုပါက "
                f"မိဘပြည်သူများ၏ လုံခြုံရေးအတွက် အောက်ပါအချက်များကို သတိပြုရန် လိုအပ်ပါသည်။\n\n"
                f"၁။ Profile တွင် မိမိ၏ပုံအစစ်မှန်ကို မတင်ထားရန်။\n"
                f"၂။ ဖုန်းနံပါတ်ကို ဖျောက်ထားရန်။\n"
                f"၃။ မိမိ၏တည်နေရာကို public chat သိုမဟုတ် DM တွင် မဖော်ပြရန်။"
                f"၄။ DMတွင်ဖြစ်စေ၊Groupထဲတွင်ဖြစ်စေ မိမိမသိသော Link များကို မနှိပ်မိရန်သတိထားပါ။"
                f"၄။ သတင်းပေးပိုလိုပါက admin များထံသို DM မှတစ်ဆင့် ဆက်သွယ်သတင်းပေးရန်။\n\n"
                f"မိဘပြည်သူများအနေဖြင့် -\n"
                f"• စကစ၏ ယုတ်မာရက်စက်မှုများ\n"
                f"• ဧည့်စားရင်းစစ်သတင်းများ\n"
                f"• စကစ၏ လှုပ်ရှားမှုသတင်းများ\n"
                f"• စစ်မှုထမ်းရန်ဖမ်းဆီးခေါ်ဆောင်မှုများ\n"
                f"တိုကို သတင်းပေးချင်ပါက ⤵️\n"
                f"/admin ကိုနှိပ်ပြီး သတင်းပေးပါ။"
            )

      
            await update.message.reply_text(welcome_message)

    except Exception as e:
        logger.error(f"Welcome error: {e}")

# ✅ Link Filter with 3-strike rule
async def filter_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    username = update.message.from_user.full_name
    text = update.message.text.lower()
    blocked_patterns = [r'http[s]?://', r'www\.', r'\.com', r't\.me/', r'@\w+']

    if any(re.search(pattern, text) for pattern in blocked_patterns):
        try:
            await update.message.delete()

            # Warning count
            if user_id not in user_warnings:
                user_warnings[user_id] = 0
            user_warnings[user_id] += 1

            if user_warnings[user_id] == 1:
                warning_msg = f"⚠️ {username}, Admin ခွင့်ပြုချက်မရှိပဲ Linkပေးပို့ရန်တားမြစ်ထားသည်။• Warns now: (1/3) ❕"
            elif user_warnings[user_id] == 2:
                warning_msg = f"⚠️ {username}, နောက်တစ်ကြိမ် Link ပို့မယ်ဆို mute လုပ်ပါမယ်! (2/3)"
            else:
                # 3rd time → mute 48 hours
                await context.bot.restrict_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=update.message.date + timedelta(hours=48)
                )
                warning_msg = f"🚫 {username} ကို 48 နာရီ mute လုပ်လိုက်ပါပြီ! (3/3)"

            sent_msg = await update.message.reply_text(warning_msg)
            await sent_msg.delete(delay=10)

        except Exception as e:
            logger.error(f"Error in filter_links: {e}")

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules_text = """📜 <b>အုပ်စုစည်းမျဉ်းများ</b>:
1. လောင်းကစားကြော်ငြာများ၊ refer မပြုလုပ်ပါနဲ့။
2. Groupအတွင်းသို့ Link မပို့ရ။
3. တော်လှန်ရေးနှင့်ပတ်သတ်သောအကြောင်းအရာများကို လွတ်လပ်စွာ ဆွေးနွေးနိုင်ပါသည်။
4. အခြား Group member များကို မညှိုးမရှိုင်းစေပါ။
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

# ✅ Ban user by username or ID
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ သင့်အနေနဲ့ admin ဖြစ်ရပါမည်။")
        return

    if not context.args:
        await update.message.reply_text("အသုံးပြုနည်း: /ban <username or user_id> [အကြောင်းရင်း]")
        return

    target = context.args[0]
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "စည်းမျဉ်းချိုးမှု"

    try:
        if target.startswith("@"):
            # Get user by username
            chat = update.effective_chat
            member = await context.bot.get_chat_member(chat.id, target)
            user_id = member.user.id
        else:
            user_id = int(target)

        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text(f"🚫 User {target} ကို Ban လုပ်ပြီးပါပြီ။\nအကြောင်းရင်း: {reason}")
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

# ✅ Block forwarded messages
async def block_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message and update.message.forward_origin:
            await update.message.delete()
            warning_msg = await context.bot.send_message(
                chat_id=update.message.chat.id,
                text=f"⚠️ {update.message.from_user.mention_html()}, Group ထဲကို Forward message မပို့နိုင်ပါ။",
                parse_mode=ParseMode.HTML
            )
            await warning_msg.delete(delay=10)
    except Exception as e:
        logger.error(f"Forward block error: {e}")


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
