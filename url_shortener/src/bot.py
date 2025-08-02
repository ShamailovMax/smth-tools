import os
import logging

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

from messages import (
    WELCOME_MESSAGE, 
    HELP_MESSAGE, 
    ERROR_MESSAGES,
    STATUS_MESSAGES
)

from bot_utils import looks_like_url, get_success_message


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = f"{os.getenv('BOT_TOKEN')}"
API_URL = "http://localhost:5000"

def looks_like_url(text):
    text = text.strip()
    return text.startswith(('http://', 'https://')) and len(text) > 10

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_MESSAGE, parse_mode='Markdown')

async def shorten_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.strip()
    
    if not looks_like_url(user_message):
        await update.message.reply_text(ERROR_MESSAGES['not_url'])
        return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # request sending to flask
        response = requests.post(
            f"{API_URL}/shorten",
            json={"url": user_message},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            
            result_message = get_success_message(
                short_url=data['short_url'],
                original_url=data['original_url'],
                is_existing=data.get('existing', False)
            )
            await update.message.reply_text(result_message, parse_mode='Markdown')
            
        elif response.status_code == 400:
            # validation error from flask API
            error_data = response.json()
            await update.message.reply_text(
                f"❌ {error_data.get('error', 'Неизвестная ошибка')}"
            )
            
        else:
            # other errors
            await update.message.reply_text(ERROR_MESSAGES['server_error'])
            
    except requests.exceptions.ConnectionError:
        await update.message.reply_text(ERROR_MESSAGES['connection_error'])
        
    except requests.exceptions.Timeout:
        await update.message.reply_text(ERROR_MESSAGES['timeout_error'])
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text(ERROR_MESSAGES['unexpected_error'])

async def handle_non_url_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """not url messages handler"""
    await update.message.reply_text(ERROR_MESSAGES['non_url_message'])

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'^https?://'), 
        shorten_url
    ))
    
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_non_url_message
    ))
    
    print("🤖 Telegram bot запущен...")
    print("Убедитесь, что Flask API работает на http://localhost:5000")
    application.run_polling()


if __name__ == '__main__':
    main()