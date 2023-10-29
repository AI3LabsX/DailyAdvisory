"""
The module contains handlers that respond to commands from bot users

Handlers:
    start_cmd_from_admin_handler    - response to the /start command from the bot administrator
    start_cmd_from_user_handler     - response to the /start command from the bot user
    help_cmd_handler                - response to the /help command

Note:
    Handlers are imported into the __init__.py package handlers,
    where a tuple of HANDLERS is assembled for further registration in the application
"""
# TODO: Do a data collection like in WeList bot
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackContext, CallbackQueryHandler

from tgbot.config import BOT_LOGO
from tgbot.utils.filters import is_admin_filter
from tgbot.utils.templates import template

# New questions and options
USER_QUESTIONS = [
    "What nickname or name should I use to address you?",
    "Which topic are you interested in?",
    "How often do you need advice?",
    "Which personality do you prefer for the bot?",
    "What's your current level on the chosen topic?"
]

TOPIC_OPTIONS = [
    "Personal Development", "Crypto", "AI", "Development", "Sport", "Other"
]

ADVICE_FREQUENCY_OPTIONS = [
    "Once an hour", "Once a day", "3 times a day", "Once a week", "Other"
]

PERSONALITY_OPTIONS = [
    "Male", "Female"
]

LEVEL_OPTIONS = [
    "Beginner", "Intermediate", "Advanced"
]


async def start_cmd_from_admin(update: Update, context: CallbackContext) -> None:
    """Handles command /start from the user"""
    username: str = update.message.from_user.first_name

    welcome_message = f"👋 Hello, {username if username else 'user'}! What would you like to do?"

    buttons = [
        [InlineKeyboardButton(text="Add Topic", callback_data="add_topic"),
         InlineKeyboardButton(text="Add New User", callback_data="add_new_user")]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text=welcome_message, reply_markup=keyboard)


# TODO: Adjust
async def start_cmd_from_user(update: Update, context: CallbackContext) -> None:
    """Handles command /start from the user"""
    username: str = update.message.from_user.first_name

    welcome_message = f"👋 Hello, {username if username else 'user'}! What would you like to do?"
    buttons = [
        [KeyboardButton(text="Add Topic"), KeyboardButton(text="Add New User"), KeyboardButton(text="Edit Users")]
    ]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(text=welcome_message, reply_markup=keyboard)

    # Set the conversation state to 'idle'
    context.user_data['conversation_state'] = 'idle'


async def add_topic(update: Update, context: CallbackContext) -> None:
    """Handles the 'Add Topic' command."""
    chat_id = update.message.chat_id
    # Initialize question index for the new topic questions
    context.user_data['topic_question_index'] = 0
    # Send the first question directly
    await context.bot.send_message(chat_id=chat_id, text=USER_QUESTIONS[1],
                                   reply_markup=ReplyKeyboardMarkup([TOPIC_OPTIONS], one_time_keyboard=True,
                                                                    resize_keyboard=True))


async def add_new_user(update: Update, context: CallbackContext) -> None:
    """Handles the 'Add New User' command."""
    chat_id = update.message.chat_id
    # Initialize question index for the new user questions
    context.user_data['user_question_index'] = 0
    # Send the first question directly
    await context.bot.send_message(chat_id=chat_id, text=USER_QUESTIONS[0])


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles command /help from the user

    Note:
        In this handler as an example, we will use the template renderer to format the response message
    """
    data: dict = {
        "framework_url": "https://python-telegram-bot.org",
        "licence_url": "https://github.com/rin-gil/python-telegram-bot-template/blob/master/LICENCE",
        "author_profile_url": "https://www.instagram.com/rexxar.ai/",
        "author_email": "riharex420@gmail.com",
    }
    caption: str = await template.render(template_name="help_cmd.jinja2", data=data)
    await update.message.reply_photo(photo=BOT_LOGO, caption=caption)


async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data

    if data == "add_topic":
        await add_topic(update, context)
    elif data == "add_new_user":
        await add_new_user(update, context)
    # ... handle other button presses if needed

    # Always answer the callback query to prevent the "loading" animation on the button
    await query.answer()


async def exit_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Exit the chat and return to the main menu."""
    await update.message.reply_text(text="Exiting the chat. Returning to the main menu.")
    # Set the conversation state to 'idle'
    context.user_data['conversation_state'] = 'idle'
    await start_cmd_from_user(update, context)


# Creating handlers
start_cmd_from_admin_handler: CommandHandler = CommandHandler(
    command="start", callback=start_cmd_from_admin, filters=is_admin_filter
)

start_cmd_from_user_handler: CommandHandler = CommandHandler(command="start", callback=start_cmd_from_user)
help_cmd_handler: CommandHandler = CommandHandler(command="help", callback=help_cmd)
exit_cmd_handler: CommandHandler = CommandHandler(command="exit", callback=exit_chat)
add_topic_handler: CommandHandler = CommandHandler(command="add_topic", callback=add_topic)
add_new_user_handler: CommandHandler = CommandHandler(command="add_new_user", callback=add_new_user)
button_handler: CallbackQueryHandler = CallbackQueryHandler(button_handler)
