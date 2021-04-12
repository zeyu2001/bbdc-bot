from telegram.ext import Updater, CommandHandler, Filters
import configparser
import sys
import signal
import telegram

import callbacks

CONFIG_FILE = "config.ini"

config = configparser.ConfigParser()

try:
    config.read(CONFIG_FILE)
    api_token = config['telegram']['api_token']
    telegram_id = int(config['telegram']['user_id'])
    bbdc_username = config['bbdc']['username']
    bbdc_password = config['bbdc']['password']
    bbdc_id = config['bbdc']['acct_id']

except configparser.ParsingError:
    print("CONFIG ERROR: Cannot parse config.ini.")
    sys.exit(1)

except KeyError:
    print("CONFIG ERROR: Required sections or options not found.")
    sys.exit(1)

except configparser.Error:
    print("CONFIG ERROR: Please check the config.ini file.")
    sys.exit(1)


def sigterm_handler(signum, frame):
    print("EXITING...")

    for chat_id, bot in callbacks.my_bots.items():
        bot.send_message(
            chat_id=chat_id,
            text='<b>Heroku dyno restarting:</b> Send /start in 5 minutes to restart the scheduled search.',
            parse_mode=telegram.ParseMode.HTML
        )
        print("[INFO] Sent restart message.")
    sys.exit(0)


def main():

    updater = Updater(api_token, user_sig_handler = sigterm_handler)
    dp = updater.dispatcher

    # Limit access to a specific user (based on config.ini)
    dp.add_handler(CommandHandler('start', callbacks.start, Filters.user(user_id=telegram_id), pass_job_queue=True))
    dp.add_handler(CommandHandler('stop', callbacks.stop, Filters.user(user_id=telegram_id), pass_job_queue=True))
    dp.add_handler(CommandHandler('months', callbacks.months, Filters.user(user_id=telegram_id), pass_job_queue=True))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()