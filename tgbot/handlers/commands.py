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
from telegram.ext import ContextTypes, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters

from tgbot.config import BOT_LOGO
from tgbot.handlers.io_tools import store_user_data
from tgbot.handlers.messages import ask_question
from tgbot.utils.filters import is_admin_filter
from tgbot.utils.templates import template

# New questions and options
USER_QUESTIONS = [
    "Which topic are you interested in?",
    "How often do you need advice?",
    "Which personality do you prefer for the bot?",
    "What's your current level on the chosen topic?"
]
KEYS = [
    "NAME",
    "TOPIC",
    "FREQUENCY",
    "PERSONA",
    "LEVEL"
]

TOPIC_OPTIONS = [
    ["Personal Development", "Crypto"],
    ["AI", "Development"],
    ["Sport", "Other"]
]

ADVICE_FREQUENCY_OPTIONS = [
    ["Once an hour", "Once a day"],
    ["3 times a day", "Once a week"],
    ["Other"]
]

PERSONALITY_OPTIONS = [
    ["Male", "Female"]
]

LEVEL_OPTIONS = [
    ["Beginner", "Intermediate", "Advanced"]
]
# Mapping questions to their options
QUESTION_OPTIONS = {
    "Which topic are you interested in?": TOPIC_OPTIONS,
    "How often do you need advice?": ADVICE_FREQUENCY_OPTIONS,
    "Which personality do you prefer for the bot?": PERSONALITY_OPTIONS,
    "What's your current level on the chosen topic?": LEVEL_OPTIONS
}


async def start_cmd_from_admin(update: Update, context: CallbackContext) -> None:
    """Handles command /start from the user"""
    username: str = update.message.from_user.first_name

    welcome_message = f"👋 Hello, {username if username else 'user'}! What would you like to do?"

    # Check if the user has already added a topic (this is a placeholder, you'll need to check the database)
    has_added_topic = False  # Placeholder, replace with actual check

    if has_added_topic:
        buttons = [
            [InlineKeyboardButton(text="Add Topic", callback_data="add_topic"),
             InlineKeyboardButton(text="Advice", callback_data="advice"),
             InlineKeyboardButton(text="QA", callback_data="qa")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text="Add Topic", callback_data="add_topic")]
        ]

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text=welcome_message, reply_markup=keyboard)
    # Set the conversation state to 'idle'
    context.user_data["conversation_state"] = "idle"


# TODO: Adjust
async def start_cmd_from_user(update: Update, context: CallbackContext) -> None:
    """Handles command /start from the user"""
    username: str = update.message.from_user.first_name

    welcome_message = f"👋 Hello, {username if username else 'user'}! What would you like to do?"

    # Check if the user has already added a topic (this is a placeholder, you'll need to check the database)
    has_added_topic = False  # Placeholder, replace with actual check

    if has_added_topic:
        buttons = [
            [InlineKeyboardButton(text="Add Topic", callback_data="add_topic"),
             InlineKeyboardButton(text="Advice", callback_data="advice"),
             InlineKeyboardButton(text="QA", callback_data="qa")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text="Add Topic", callback_data="add_topic")]
        ]

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text=welcome_message, reply_markup=keyboard)
    # Set the conversation state to 'idle'
    context.user_data["conversation_state"] = "idle"


CONFIRM_DATA = "confirm_data"
EDIT_DATA = "edit_data"
QUESTION_INDEX = 0


async def display_summary(update: Update, context: CallbackContext) -> None:
    chat_id = (
        update.message.chat_id
        if update.message
        else update.callback_query.message.chat_id
    )
    summary = "\n".join(
        [f"{key}: {context.user_data['data'].get(key, 'N/A')}" for key in KEYS]
    )

    buttons = [
        [
            InlineKeyboardButton(text="Confirm", callback_data=CONFIRM_DATA),
            InlineKeyboardButton(text="Edit", callback_data=EDIT_DATA),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Here's the summary of your data:\n\n{summary}",
        reply_markup=keyboard,
    )


async def edit_data_selection(update: Update, context: CallbackContext) -> None:
    chat_id = update.callback_query.message.chat_id
    buttons = [[InlineKeyboardButton(text=key, callback_data=key)] for key in KEYS]
    keyboard = InlineKeyboardMarkup(buttons)

    await context.bot.send_message(
        chat_id=chat_id,
        text="Which data would you like to edit?",
        reply_markup=keyboard,
    )


async def edit_data_input(update: Update, context: CallbackContext, key: str) -> None:
    chat_id = (
        update.callback_query.message.chat_id
        if update.callback_query
        else update.message.chat_id
    )
    context.user_data["editing_key"] = key

    question_index = (
        KEYS.index(key) - 1
        if key != "NAME"
        else KEYS.index(key)
    )
    print(question_index)
    question = USER_QUESTIONS[question_index]
    print(question)
    options = QUESTION_OPTIONS.get(question)
    print(options)
    if options and key != "NAME":
        keyboard = ReplyKeyboardMarkup(
            options, one_time_keyboard=True, resize_keyboard=True
        )
        await context.bot.send_message(
            chat_id=chat_id, text=USER_QUESTIONS[question_index], reply_markup=keyboard
        )
    elif key == "NAME":
        await context.bot.send_message(chat_id=chat_id, text="What nickname or name should I use to address you?:")
    else:
        await context.bot.send_message(chat_id=chat_id, text=USER_QUESTIONS[question_index])


async def send_question(update: Update, context: CallbackContext) -> None:
    question_index = context.user_data.get(QUESTION_INDEX, 0)
    """Send the next question to the user."""
    chat_id = (
        update.message.chat_id
        if update.message
        else update.callback_query.message.chat_id
    )

    # Get the current question index from context.user_data or initialize it to 0


    editing_key = context.user_data.get("editing_key", None)
    if editing_key:
        # Store the edited value
        context.user_data["data"][editing_key] = update.message.text
        # Debugging statement
        print(f"Editing key: {editing_key}, Value: {update.message.text}")
        # Reset editing_key
        context.user_data["editing_key"] = None
        # Display the summary again
        await display_summary(update, context)
        return
    if (
            update.message
            and 0 <= question_index < len(KEYS)
    ):
        context.user_data["data"][KEYS[question_index]] = update.message.text
    # Check if we've asked all questions
    if question_index < len(USER_QUESTIONS):
        current_question = USER_QUESTIONS[question_index]
        options = QUESTION_OPTIONS.get(current_question)
        if options:
            keyboard = ReplyKeyboardMarkup(
                options, one_time_keyboard=True, resize_keyboard=True
            )
            await context.bot.send_message(
                chat_id=chat_id, text=current_question, reply_markup=keyboard
            )
        else:
            await context.bot.send_message(chat_id=chat_id, text=current_question)

        # Increment the question index for the next question
        context.user_data[QUESTION_INDEX] = question_index + 1
    elif question_index == len(USER_QUESTIONS):  # After the last question
        await display_summary(update, context)
        return
    else:
        # Reset the question index and inform the user that all questions have been asked
        context.user_data[QUESTION_INDEX] = 0
        await context.bot.send_message(chat_id=chat_id, text="Thank you for answering all the questions!")


async def get_data_from_user(update, context):
    chat_id = (
        update.message.chat_id
        if update.message
        else update.callback_query.message.chat_id
    )
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    data = context.user_data['data']

    # Store data in the database
    # store_user_data(user_id, data)

    # Send a message to the user with further instructions
    message = (
        f"Now, advices will come to you with frequency: {data['FREQUENCY']}.\n"
        "To ask a question about the topic, use command `/ask`.\n"
        "To get a random advice from the topic, use command `/advice`."
    )
    await context.bot.send_message(chat_id=chat_id, text=message)


async def add_topic(update: Update, context: CallbackContext) -> None:
    """Handles the 'Add Topic' command."""
    query = update.callback_query
    await query.answer()
    if query.data == "add_topic":
        # Initialize question index and data dictionary
        context.user_data[QUESTION_INDEX] = 0
        context.user_data["data"] = {}
        context.user_data["asking_questions"] = True  # Set the flag
        await context.bot.send_message(
            chat_id=query.message.chat_id, text="What nickname or name should I use to address you?:"
        )
    elif query.data == CONFIRM_DATA:
        await get_data_from_user(update, context)

    elif query.data == EDIT_DATA:
        await edit_data_selection(update, context)

    elif query.data in KEYS:
        await edit_data_input(update, context, query.data)
    else:
        await send_question(update, context)
    # Always answer the callback query to prevent the "loading" animation on the button



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

button_handler: CallbackQueryHandler = CallbackQueryHandler(add_topic)
add_topic_handler: MessageHandler = MessageHandler(
    filters.TEXT & ~filters.COMMAND, send_question
)
