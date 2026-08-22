import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import MenuButtonWebApp, WebAppInfo, MenuButtonDefault

from app.config import settings
from app.bot.handlers import router

logger = logging.getLogger(__name__)

bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)

dp = Dispatcher()
dp.include_router(router)


async def setup_bot_menu():
    """Setup Telegram native menu button (near input bar) for Mini App."""
    try:
        if settings.WEBAPP_URL and settings.WEBAPP_URL.startswith("https://"):
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text="Starting Task Tracker Bot",
                    web_app=WebAppInfo(url=settings.WEBAPP_URL)
                )
            )
            logger.info(f"Configured Telegram native input bar MenuButton -> {settings.WEBAPP_URL}")
        else:
            logger.info("WEBAPP_URL is not HTTPS yet. Set an HTTPS URL in .env to enable the native 'Starting Task Tracker Bot' input bar button.")
    except Exception as e:
        logger.warning(f"Could not configure native menu button: {e}")
