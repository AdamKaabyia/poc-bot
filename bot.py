import logging
import os
from dotenv import load_dotenv
import telegram
from telegram.constants import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, ApplicationBuilder

# Load environment variables from .env file
load_dotenv()
token = os.getenv('TOKEN')

print(token)

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
    await update.message.reply_text('thw commands are:\n'
                                    '/scream\n'
                                    '/start\n'
                                    '/whisper\n'
                                    '/menu\n')
    pass

def echo(update: telegram.Update, context: CallbackContext) -> None:
    """Echo the user message."""
    logger.info(f'{update.message.from_user.first_name} wrote {update.message.text}')
    if screaming and update.message.text:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=update.message.text.upper(),
            entities=update.message.entities
        )
    else:
        update.message.copy(update.message.chat_id)

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

def button_tap(update: telegram.Update, context: CallbackContext) -> None:
    """Handles inline button taps."""
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

    query.answer()
    query.edit_message_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=markup
    )

def main() -> None:
    """Start the bot."""
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

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.add_handler(CallbackQueryHandler(button_tap))

    application.add_error_handler(error)

    application.run_polling()

if __name__ == '__main__':
    main()