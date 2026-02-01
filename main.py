import os
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from fastapi import FastAPI, Request
import uvicorn

from config import BOT_TOKEN
from database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

application = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Bifinance Customer Support\n\n"
        "This is the **official** support bot.\n"
        "Support never messages first.\n\n"
        "Use /help for commands.\n"
        "Please describe your issue."
    )
    # Later: start FSM form here

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid == config.OWNER_ID or uid in config.AGENT_IDS:  # later from DB
        text = (
            "Agent commands:\n"
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
