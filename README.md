# bbdc-bot
 
Telegram bot for fetching Bukit Batok Driving Centre practical slots.

## Usage

You need to create a Telegram bot for yourself. Refer to the Telegram API [documentation](https://core.telegram.org/bots) for moreinformation.

Edit the [`config.ini`](config.ini) file.

### Telegram

- `api_token`: Your Telegram bot's API token
- `user_id`: Your Telegram user ID. Only this user can send or receive messages from the bot.

### BBDC

- `username`: Your BBDC username
- `password`: Your BBDC password
- `acct_id`: Your BBDC account ID. This should be shown in your BBDC profile.

## Common Issues

BBDC might block Heroku IP addresses. When I was using this bot, I used the [Fixie addon](https://elements.heroku.com/addons/fixie) for Heroku to route outbound requests through a different IP.
