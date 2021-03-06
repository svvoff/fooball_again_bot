from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler
from telegram.ext.filters import Filters
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import json
import datetime as dt
import unicodedata
import random

# Logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Read settings
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv('TOKEN')

class App:
    def __init__(self, token):
        self.bot_name = "football_again_bot"
        self.updater = Updater(token=token)
        self.update_triggers()
        self.update_answers()
        self.messages_counter = 3
        self.last_handled_message_date = None
        self.inter_messages_dealy_seconds = 10
    
    def run(self):
        updater = self.updater
        updater.dispatcher.add_handler(CommandHandler('update_triggers', self.update_triggers_handler))
        updater.dispatcher.add_handler(CommandHandler('update_answers', self.update_answers_handler))
        updater.dispatcher.add_handler(MessageHandler(Filters.all, self.messages_handler))

        updater.start_polling()
        updater.idle()


    def update_triggers_handler(self, update: Update, context: CallbackContext) -> None:
        self.update_triggers()
        message = update.message
        new_triggers = "\n".join(self.triggers)
        message.reply_text("Triggers were updated")
        context.bot.send_message(chat_id=update.effective_chat.id, text=new_triggers)

    def update_answers_handler(self, update: Update, context: CallbackContext) -> None:
        self.update_answers()
        message = update.message
        new_answers = "\n\n".join(self.answers)
        message.reply_text("Answers were updated")
        context.bot.send_message(chat_id=update.effective_chat.id, text=new_answers)
    
    def messages_handler(self, update: Update, context: CallbackContext) -> None:
        message = update.message

        reply_to_message = message.reply_to_message
        if reply_to_message and reply_to_message.from_user.username == self.bot_name:
            self.replies_handler(update, context)
            return
        
        text = None
        is_emoji = False
        if message.text:
            text = message.text.lower()
        elif message.dice:
            is_emoji = True
            text = message.dice.emoji

        if text == None:
            return

        if is_emoji:
            for emoji in self.emojis:
                should_break = False
                for e in emoji:
                    if text.count(e) > 0:
                        should_break = True
                        self.reply_if_needed(update = update, context = context)
                        break
                if should_break:
                    break
        else:
            for trigger in self.triggers:
                if trigger in text:
                    self.reply_if_needed(update = update, context = context)
                    break
                
    def replies_handler(self, update: Update, context: CallbackContext) -> None:
        message = update.message
        message.reply_text("А ну отъебись от меня пес паршивый! Не видишь работаю!? Сидит, блядь, выписывает тут!")
    
    def reply_if_needed(self, update: Update, context: CallbackContext) -> None:
        message = update.message
        if self.last_handled_message_date != None:
            diff = (message.date - self.last_handled_message_date).total_seconds()
            if diff < self.inter_messages_dealy_seconds:
                return
            else:
                self.last_handled_message_date = None

        self.messages_counter -= 1
        if self.messages_counter <= 0:
            self.messages_counter = 10000000
            self.last_handled_message_date = message.date
        msg = random.choice(self.answers)
        message.reply_text(msg)

    def update_triggers(self):
        with open('triggers.json') as json_file:
            data = json.load(json_file)
            self.triggers = data['triggers']
            self.emojis = data['emojis']
    
    def update_answers(self):
        with open('answers.json') as json_file:
            data = json.load(json_file)
            self.answers = data

app = App(TOKEN)
app.run()
    

