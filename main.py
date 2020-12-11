from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler
from telegram.ext.filters import Filters
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import json

# Logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Read settings
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv('TOKEN')


def get_triggers() -> list:
    with open('footbick.json') as json_file:
        data = json.load(json_file)
        return data['triggers']

TRIGGERS = get_triggers()

# Run
updater = Updater(token=TOKEN)

def update_triggers(update: Update, context: CallbackContext) -> None:
    TRIGGERS = get_triggers()
    message = update.message
    new_triggers = "\n".join(TRIGGERS)
    message.reply_text("Triggers were updated")
    context.bot.send_message(chat_id=update.effective_chat.id, text=new_triggers)
    
def messages_handler(update: Update, context: CallbackContext) -> None:
    message = update.message
    text = message.text.lower()
    for trigger in TRIGGERS:
        if trigger in text:
            message.reply_text("Опять футбик")
            break

    
updater.dispatcher.add_handler(CommandHandler('update_triggers', update_triggers))
updater.dispatcher.add_handler(MessageHandler(Filters.all, messages_handler))

updater.start_polling()
updater.idle()
