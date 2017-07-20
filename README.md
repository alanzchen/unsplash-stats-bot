# unsplash-stats-bot
A telegram bot that monitors your Unsplash stats.

## Running your own server

Open `bot.py` and edit `telegram_token` & `unsplash_api_key` to your own credentials.


Then, on a server, simply run:

```
$ pip install python-telegram-bot requests --upgrade
$ python bot.py
```

You may need `nohup` or `screen` to keep it running in the background.

## Credits

Modified from a example from [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py).