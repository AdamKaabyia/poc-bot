import pytest
from telegram import Update, User, Chat, Message
from telegram.ext import CallbackContext

from bot import test  # Ensure this import reflects the actual path to your bot.py file or module

@pytest.fixture
def update():
    # Mock an Update object with a Message
    user = User(id=123, is_bot=False, first_name="Test User")
    chat = Chat(id=123, type='private')
    message = Message(message_id=42, date=None, chat=chat, text="/test", from_user=user)
    return Update(update_id=1, message=message)

@pytest.fixture
def context(update):  # Passing the 'update' fixture as a parameter
    # Mock a CallbackContext
    return CallbackContext(dispatcher=None, update=update, bot=None, user_data={}, chat_data={}, match=None)

def test_test_command(update, context, capsys):  # capsys is a pytest fixture to capture print statements
    # Call the test function which should trigger a message
    # Note: This assumes `test` function sends a message directly, but it actually replies, which needs a different approach to capture.
    test(update, context)
    captured = capsys.readouterr()  # Capture what has been 'printed' or 'output'
    assert 'Test command received!' in captured.out  # Check if the expected text is in output
