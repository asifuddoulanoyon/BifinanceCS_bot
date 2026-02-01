# main.py
import os
import logging
import asyncio
import sys
import traceback
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
import uvicorn
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ────────────────────────────────────────────────
# Logging - very important for Render debugging
# ────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(name)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────
# Environment variables
# ────────────────────────────────────────────────

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", "10000"))
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))  # your telegram id

if not BOT_TOKEN:
    logger.critical("BOT_TOKEN environment variable is missing!")
    sys.exit(1)

if OWNER_ID == 0:
    logger.warning("OWNER_ID not set - owner commands will be disabled")

logger.info(f"Starting with BOT_TOKEN (len={len(BOT_TOKEN)}), PORT={PORT}, OWNER_ID={OWNER_ID}")

# ────────────────────────────────────────────────
# Telegram Application
# ────────────────────────────────────────────────

application = Application.builder().token(BOT_TOKEN).build()

# ────────────────────────────────────────────────
# Basic handlers
# ────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = (
        "👋 Welcome to **Bifinance Customer Support**\n\n"
        "This is the **only official** support channel.\n"
        "⚠️ Real support will **never** message you first.\n\n"
        "Please tell us your problem or use /help"
    )
    await update.message.reply_text(text, disable_web_page_preview=True)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if uid == OWNER_ID:
        text = (
            "🛠 Owner / Agent commands:\n\n"
            "/start - welcome message\n"
            "/help - this message\n"
            "/status - show bot status\n"
            "\n(Full ticket system coming soon)"
        )
    else:
        text = (
            "Help for users:\n\n"
            "/start - begin support\n"
            "Just write your message after ticket is created\n"
            "Support team will reply soon."
        )
    await update.message.reply_text(text)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Temporary echo handler – will be replaced with ticket routing"""
    text = update.message.text
    if text:
        await update.message.reply_text(f"Received:\n{text}\n\n(Support routing not active yet)")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling update:", exc_info=context.error)


# ────────────────────────────────────────────────
# Register handlers
# ────────────────────────────────────────────────

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

application.add_error_handler(error_handler)

# ────────────────────────────────────────────────
# FastAPI app for webhook
# ────────────────────────────────────────────────

app = FastAPI(title="Bifinance Support Bot Webhook")

@app.get("/")
async def root():
    return {
        "status": "online",
        "time": datetime.utcnow().isoformat(),
        "bot": (await application.bot.get_me()).username
    }


@app.post("/webhook")
async def webhook(request: Request):
    if request.headers.get("content-type") == "application/json":
        json_data = await request.json()
        update = Update.de_json(json_data, application.bot)
        if update:
            await application.process_update(update)
            return {"ok": True}
    raise HTTPException(status_code=400, detail="Bad request")


@app.on_event("startup")
async def startup_event():
    try:
        me = await application.bot.get_me()
        logger.info(f"Bot started: @{me.username} (ID: {me.id})")

        # Set webhook
        hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
        if not hostname:
            logger.error("RENDER_EXTERNAL_HOSTNAME not available!")
            return

        webhook_url = f"https://{hostname}/webhook"
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook successfully set to: {webhook_url}")

    except Exception as e:
        logger.critical("Startup failed!", exc_info=e)
        raise


# ────────────────────────────────────────────────
# Main entry point
# ────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info(f"Starting uvicorn on 0.0.0.0:{PORT}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        workers=1,
        timeout_keep_alive=65
    )            "Agent commands:\n"
            "/mycases - show my assigned cases\n"
            "/take <case_id> - take a case\n"
            "/close <case_id> - close case\n"
            "/transfer <case_id> @username - transfer\n"
            "/add_agent <user_id or @username> - owner only"
        )
    else:
        text = "User help: just write your message after ticket created."
    await update.message.reply_text(text)

# Placeholder for user messages
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Later: check if has open case, forward to agent
    await update.message.reply_text("Your message received. Support will reply soon.")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

# Webhook setup for Render
app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()
    webhook_url = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/webhook"
    await application.bot.set_webhook(url=webhook_url)
    logger.info("Webhook set")

@app.post("/webhook")
async def webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, application.bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/")
async def health():
    return {"status": "alive"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
