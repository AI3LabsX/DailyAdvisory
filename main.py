"""Launches the bot"""

from telegram.constants import ParseMode
from telegram.ext import AIORateLimiter, Application, Defaults

from tgbot.handlers import HANDLERS
from tgbot.handlers.db_init import init_db
from tgbot.handlers.errors import error_handler
from tgbot.utils.bot_commands import set_default_commands
from tgbot.utils.environment import env
from tgbot.utils.logger import logger


async def on_startup(application: Application) -> None:
    """
    The function that runs when the bot starts, before the application.run_polling()
    In this example, the function sets the default commands for the bot
    """
    await set_default_commands(application=application)


# def install_playwright_browsers():
#     """Install Playwright browsers using subprocess."""
#     try:
#         logger.info("Installing Playwright browsers...")
#         subprocess.run(["playwright", "install"], check=True)
#         logger.info("Playwright browsers installed successfully.")
#     except subprocess.CalledProcessError:
#         logger.critical("Failed to install Playwright browsers.")
#         raise


def register_all_handlers(application: Application) -> None:
    """Registers handlers"""
    application.add_handlers(handlers=HANDLERS)  # type: ignore
    application.add_error_handler(callback=error_handler)


def start_bot() -> None:
    init_db()
    """Launches the bot"""

    # Create the Application and pass it your bot's token.
    application: Application = (
        Application.builder()
        .token(token=env.get_bot_token())
        .defaults(defaults=Defaults(parse_mode=ParseMode.HTML, block=False))
        .rate_limiter(rate_limiter=AIORateLimiter(max_retries=3))
        .post_init(post_init=on_startup)
        .build()
    )

    register_all_handlers(application=application)

    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    try:
        logger.info("Starting bot")
        start_bot()
    except Exception as exc:
        logger.critical("Unhandled error: %s", repr(exc))
    finally:
        logger.info("Bot stopped!")
