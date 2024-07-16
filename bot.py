import logging
import os
import requests
from dotenv import load_dotenv
import telegram
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, ApplicationBuilder

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Store bot screaming status
screaming = False

# Pre-assign menu text
FIRST_MENU = "<b>Menu 1</b>\n\nA beautiful menu with a shiny inline button."
SECOND_MENU = "<b>Menu 2</b>\n\nA better menu with even more shiny inline buttons."

# Pre-assign button text
NEXT_BUTTON = "Next"
BACK_BUTTON = "Back"
TUTORIAL_BUTTON = "Tutorial"

FIRST_MENU_MARKUP = telegram.InlineKeyboardMarkup([[
    telegram.InlineKeyboardButton(NEXT_BUTTON, callback_data=NEXT_BUTTON)
]])
SECOND_MENU_MARKUP = telegram.InlineKeyboardMarkup([
    [telegram.InlineKeyboardButton(BACK_BUTTON, callback_data=BACK_BUTTON)],
    [telegram.InlineKeyboardButton(TUTORIAL_BUTTON, url="https://core.telegram.org/bots/api")]
])


def error(update: telegram.Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


async def start(update: telegram.Update, context: CallbackContext):
    await update.message.reply_text('The commands are:\n'
                                    '/scream\n'
                                    '/start\n'
                                    '/whisper\n'
                                    '/menu\n'
                                    '/generate\n'
                                    '/store\n')
    pass


async def get_response_from_server(endpoint: str, payload: dict) -> str:
    server_addr = os.getenv('SERVER_ADDR')

    if not server_addr:
        raise EnvironmentError("SERVER_ADDR environment variable not set")

    url = f"http://{server_addr}{endpoint}"
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["message"]
    except requests.RequestException as e:
        return f"An error occurred: {e}"


async def log_interaction(user_query: str, bot_response: str):
    server_addr = os.getenv('SERVER_ADDR')

    if not server_addr:
        raise EnvironmentError("SERVER_ADDR environment variable not set")

    url = f"http://{server_addr}/log_interaction"
    try:
        response = requests.post(url, json={"user_query": user_query, "bot_response": bot_response})
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to log interaction: {e}")


async def echo(update: telegram.Update, context: CallbackContext) -> None:
    """Echo the user message."""
    user_message = update.message.text
    logger.info(f'{update.message.from_user.first_name} wrote {user_message}')

    #response = await get_response_from_server("/ask", {"question": user_message})
    response =user_message
    if screaming:
        response = response.upper()

    await update.message.reply_text(response)
    await log_interaction(user_message, response)


async def scream(update: telegram.Update, context: CallbackContext) -> None:
    """Activates screaming mode."""
    global screaming
    screaming = True
    logger.info("Screaming mode activated")
    await update.message.reply_text('Screaming mode activated!')


async def whisper(update: telegram.Update, context: CallbackContext) -> None:
    """Deactivates screaming mode."""
    global screaming
    screaming = False
    logger.info("Screaming mode deactivated")
    await update.message.reply_text('Screaming mode deactivated!')


async def menu(update: telegram.Update, context: CallbackContext) -> None:
    """Sends a menu with inline buttons."""
    await context.bot.send_message(
        chat_id=update.message.from_user.id,
        text=FIRST_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=FIRST_MENU_MARKUP
    )


async def button_tap(update: telegram.Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    text = ''
    markup = None

    if data == NEXT_BUTTON:
        text = SECOND_MENU
        markup = SECOND_MENU_MARKUP
    elif data == BACK_BUTTON:
        text = FIRST_MENU
        markup = FIRST_MENU_MARKUP

    await query.answer()
    await query.edit_message_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=markup
    )


async def generate(update: telegram.Update, context: CallbackContext) -> None:
    """Generates a random number and stores it in MongoDB."""
    response = await get_response_from_server("/generate", {})
    await update.message.reply_text(response)
    await log_interaction("/generate", response)


async def store(update: telegram.Update, context: CallbackContext) -> None:
    """Stores info in MongoDB."""
    info = update.message.text.split(' ', 1)[1]
    response = await get_response_from_server("/store", {"info": info})
    await update.message.reply_text(response)
    await log_interaction("/store", response)


def main() -> None:
    load_dotenv()
    token = os.getenv('TOKEN')
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable not set")
        return

    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("scream", scream))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("whisper", whisper))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("generate", generate))
    application.add_handler(CommandHandler("store", store))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.add_handler(CallbackQueryHandler(button_tap))

    application.add_error_handler(error)

    application.run_polling()


if __name__ == '__main__':
    main()
