import redis
import configparser
import requests
import logging
from ChatGPT_HKBU import HKBU_ChatGPT
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
global redis1

def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg)

        update.message.reply_text('You have said ' + msg + ' for ' +
        redis1.get(msg) + ' times.') # .decode('UTF-8')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def set_value(update: Update, context: CallbackContext) -> None:
    """Set a value in Redis when the command /set is issued."""
    try:
        global redis1
        key = context.args[0]
        value = ' '.join(context.args[1:])
        redis1.set(key, value)
        update.message.reply_text(f'Set {key} to {value}.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <key> <value>')

def get_value(update: Update, context: CallbackContext) -> None:
    """Get a value from Redis when the command /get is issued."""
    try:
        global redis1
        key = context.args[0]
        value = redis1.get(key)
        if value:
            update.message.reply_text(f'The value for {key} is {value}.')
        else:
            update.message.reply_text(f'{key} does not exist.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /get <key>')

def delete_value(update: Update, context: CallbackContext) -> None:
    """Delete a value from Redis when the command /delete is issued."""
    try:
        global redis1
        key = context.args[0]
        result = redis1.delete(key)
        if result == 1:
            update.message.reply_text(f'Deleted {key}.')
        else:
            update.message.reply_text(f'{key} does not exist.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /delete <key>')

def hello(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /hello is issued."""
    try:
        update.message.reply_text('Good day,' + str(context.args[0]) + '!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <keyword>')


def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('configGAI.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']),
                         password=(config['REDIS']['PASSWORD']),
                         port=int(config['REDIS']['REDISPORT']),
                         decode_responses=(config['REDIS']['DECODE_RESPONSE']),
                         username=(config['REDIS']['USER_NAME']))
    # You can set this logging module, so you will know when
    # and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher


    # Dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("set", set_value))
    dispatcher.add_handler(CommandHandler("get", get_value))
    dispatcher.add_handler(CommandHandler("delete", delete_value))
    dispatcher.add_handler(CommandHandler("hello", hello))

    # Start the Bot
    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()
