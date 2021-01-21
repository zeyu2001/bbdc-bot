import telegram
import emoji
import datetime
import pytz

from bbdcscraper import BBDCScraper
from main import bbdc_username, bbdc_password

# For handling Heroku cycling
my_bots = {}
bbdc_scraper = None

# Slots to Check (0 refers to first month, 1 refers to second month, and so on)
MONTHS = [0, 1]  # Default: next 2 months (including current month)
SESSIONS = [8]      # All sessions
DAYS = [7]          # All days

# Telegram Bot
TIMEZONE = pytz.timezone("Singapore")
WELCOME_MSG = """
:wave: <b>Welcome, {}!</b>

I am {}, your personal BBDC booking assistant. 

I will automatically search for slots every 10 minutes, and update you when there is a free slot!

Here are the commands you can use:

:white_small_square: /start: Start searching for slots.
:white_small_square: /months &lt1-12&gt: Toggle number of months to search in advance.
:white_small_square: /stop: Stop searching for slots.
"""
MAX_COUNT = 5      # Maximum number of days to display


def search_slots(context: telegram.ext.CallbackContext):

    bot, job = context.bot, context.job

    # Pretend to be typing
    bot.send_chat_action(chat_id=job.context['chat_id'], action=telegram.ChatAction.TYPING)

    bbdc_scraper = job.context['scraper']
    chat = job.context['chat_id']

    now = datetime.datetime.now().astimezone(TIMEZONE)
    hour = now.hour

    try:
        bbdc_scraper.login(bbdc_username, bbdc_password)

    except Exception as e:
        print(e)
        return

    try:
        results = bbdc_scraper.get_available_slots(MONTHS, SESSIONS, DAYS)

    except Exception as e:
        print(e)
        return

    to_send = ""
    i = count = 0
    prev_date = None
    while (i < len(results) and count < MAX_COUNT):
        slot = results[i]
        
        if slot['date'] != prev_date:
            to_send += f"<b>{slot['date']}</b>\n"
            prev_date = slot['date']
            count += 1
        
        to_send += f"Session {slot['session']}: <i>{slot['starttime']}-{slot['endtime']}</i>, {slot['venue']}\n"
        
        i += 1
    
    if to_send:
        bot.send_message(
            chat_id=job.context['chat_id'],
            text=to_send,
            parse_mode=telegram.ParseMode.HTML
        )

        bot.send_message(
            chat_id=job.context['chat_id'],
            text="Book now at https://info.bbdc.sg/members-login/. Next update in 10 minutes.",
            parse_mode=telegram.ParseMode.HTML
        )

        print("[INFO] Sent available slots.")

    else:
        print("[INFO] Nothing to send.")


def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    global my_bots
    global bbdc_scraper

    if bbdc_scraper:
        return

    bot, job_queue = context.bot, context.job_queue
    my_bots[update.message.chat_id] = bot

    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

    bot.send_message(
        chat_id=update.message.chat_id,
        text=emoji.emojize(WELCOME_MSG.format(update.message.from_user.first_name, bot.name), use_aliases=True),
        parse_mode=telegram.ParseMode.HTML
    )

    bbdc_scraper = BBDCScraper()

    job_queue.run_once(search_slots, 0, name="search_slots", context={
        'chat_id': update.message.chat_id,
        'scraper': bbdc_scraper,
    })

    job_queue.run_repeating(search_slots, 600, name="search_slots", context={
        'chat_id': update.message.chat_id,
        'scraper': bbdc_scraper,
    })


def stop(update: telegram.Update, context: telegram.ext.CallbackContext):
    global bbdc_scraper

    bot, job_queue = context.bot, context.job_queue
    
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

    # Clear the job queue
    for job in job_queue.get_jobs_by_name('search_slots'):
        job.schedule_removal()

    bot.send_message(
            chat_id=update.message.chat_id,
            text="Stopped searching for slots. Start again by sending /start.",
        )

    bbdc_scraper = None

def months(update: telegram.Update, context: telegram.ext.CallbackContext):
    global MONTHS

    args, bot, job_queue = context.args, context.bot, context.job_queue

    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

    if len(args) != 1 or not args[0].isdigit() or int(args[0]) < 1 or int(args[0]) > 12:
        print("[INFO] Invalid arguments.")
        
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Invalid arguments. Please use /months <1-12>",
        )
    
    else:
        MONTHS = [i for i in range(0, int(args[0]))]
        print("[INFO] Updated months.")

        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Updated. You will now see slots for the next {args[0]} months.",
        )
