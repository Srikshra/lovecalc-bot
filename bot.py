from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from urllib.parse import quote_plus
import os

# 🔑 Read Bot token from environment variable (Railway will provide this)
TOKEN = os.environ["BOT_TOKEN"]

# 🌐 Your Netlify page
BASE_URL = "https://truelovecalc.netlify.app/love.html"

# 🧠 Store steps per user
user_data_store = {}


def calc_score(a: str, b: str) -> int:
    total = sum(ord(c) for c in (a + b).lower())
    return 40 + (total % 61)   # 40–100


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id] = {"step": 1}

    await update.message.reply_text(
        "💕 Welcome to True Love Calculator!\n\n"
        "👉 First, enter *your name*: ",
        parse_mode="Markdown",
    )


# Handle all text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    # If user did not start, treat this as /start
    if user_id not in user_data_store:
        user_data_store[user_id] = {"step": 1}
        await update.message.reply_text(
            "💕 Welcome to True Love Calculator!\n\n"
            "👉 First, enter *your name*: ",
            parse_mode="Markdown",
        )
        return

    step = user_data_store[user_id]["step"]

    # STEP 1 — get YOUR name
    if step == 1:
        user_data_store[user_id]["your_name"] = text
        user_data_store[user_id]["step"] = 2

        await update.message.reply_text(
            "💖 Nice! Now enter *your partner's* name:",
            parse_mode="Markdown",
        )
        return

    # STEP 2 — get PARTNER name, calculate, send link
    if step == 2:
        your_name = user_data_store[user_id]["your_name"]
        partner_name = text

        score = calc_score(your_name, partner_name)

        # build site link (site shows %)
        link = (
            f"{BASE_URL}?n1={quote_plus(your_name)}"
            f"&n2={quote_plus(partner_name)}&s={score}"
        )

        reply = (
            f"❤️ *{your_name}* + *{partner_name}*\n\n"
            "🔮 This calculator is 100% accurate — powered by horoscope science, "
            "name chemistry, and a tiny bit of universe magic ✨\n\n"
            "Your personalized love report is ready! 💕\n\n"
            f"👉 Tap below to view your full result:\n{link}\n\n"
            "Type /start to try again 💞"
        )

        await update.message.reply_text(reply, parse_mode="Markdown")

        # reset for next time
        user_data_store[user_id]["step"] = 1
        return


# 🚀 Run the bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
