from telegram.ext import Updater, CommandHandler, Job
import logging
import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

telegram_token = 'your telegram bot token'
unsplash_api_key = 'your application id here'

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.


def start(bot, update):
    update.message.reply_text(
        'Hi! Use /set <username> <target> to set your Unsplash username! \n <target> specifies when will I notify you. \n If left blank, your stats will not be monitored.')


def send(bot, job, text):
    """Function to send the message"""
    bot.send_message(job.context[0], text=text)


def unsplash_check(username):
    def send_request(username):
        try:
            response = requests.get(
                url="https://api.unsplash.com/users/" + username + "/statistics",
                params={
                    "quantity": "1",
                },
                headers={
                    "Authorization": "Client-ID " + unsplash_api_key,
                },
            )
            return response.json()
        except requests.exceptions.RequestException:
            logger.error('HTTP Request failed for ' + username)

    resp = send_request(username)
    try:
        views = resp['views']['total']
        return views
    except (KeyError, ValueError):
        return None


def check(bot, update, chat_data):
    if 'username' not in chat_data:
        update.message.reply_text(
            "Opps you have not set a username yet. See /help.")
    else:
        views = unsplash_check(chat_data['username'])
        if views:
            update.message.reply_text(
                "Your total photo view: " + str(views))
        else:
            update.message.reply_text(
                "An error occurred when checking your stats. Maybe we are out of API quota.")


def callback_check(bot, job):
    chat_data = job.context[1]
    logger.info("Scheduled job ran for " + str(job.context[0]))
    if 'username' in chat_data:
        username = chat_data['username']
        views = unsplash_check(username)
        if view:
            if 'target' in chat_data:
                if views < chat_data['target']:
                    return
            else:
                if views < 1234567:
                    return
        else:
            logger.error("Job for " + str(job.context[0]) + " failed. Possibly a API quota issue.")
            return
        bot.send_message(job.context[0], text="Hey, you just reached " +
                         str(views) +
                         "!")
        bot.send_message(job.context[0], text="From now on, we will stop monitoring on your stats. /unset and /set again to enable monitoring.")
        job.enabled = False
        job.schedule_removal()


def set(bot, update, args, job_queue, chat_data):
    """Adds a job to the queue"""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        username = args[0].strip()
        chat_data['username'] = username
        try:
            target = int(args[1])
            chat_data['target'] = target
            job = job_queue.run_repeating(callback_check,
                                          60,
                                          context=(chat_id, chat_data))
            chat_data['job'] = job
        except IndexError:
            target = None
        if target:
            update.message.reply_text(
                'Username successfully set! I will notify you when your view reaches ' + str(target) + '.')
        else:
            update.message.reply_text(
                'Username successfully set, but we will not monitor on your stats as you did not specify a <target>.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <username> <target>')


def unset(bot, update, chat_data):
    """Removes the job if the user changed their mind"""

    if 'job' not in chat_data:
        update.message.reply_text('You have no set a username yet.')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Username successfully unset!')


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(telegram_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))
    dp.add_handler(CommandHandler("check", check, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
