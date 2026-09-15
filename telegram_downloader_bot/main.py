"""
Bot asosiy fayli - aiogram 3.x freymvorkidan foydalanadi.
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, LOG_LEVEL, DOWNLOAD_DIR, TEMP_DIR

# Routerni handlers/start.py faylidan start_router nomi bilan import qilamiz
from handlers.start import start_router
# media.py ichida ham router nomi media_router bo'lsa:
from handlers.media import media_router  

from utils.file_utils import FileUtils

# Logging sozlamalari
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    """
    Bot ishga tushganda bajariladigan funksiyalar.
    """
    logger.info("Bot ishga tushmoqda...")
    
    # Bot ma'lumotlarini olish
    bot_info = await bot.get_me()
    logger.info(f"Bot: @{bot_info.username} ({bot_info.first_name})")
    
    # Papkalarni yaratish
    await FileUtils.ensure_dir(DOWNLOAD_DIR)
    await FileUtils.ensure_dir(TEMP_DIR)
    
    logger.info("Bot tayyor!")


async def on_shutdown(bot: Bot) -> None:
    """
    Bot to'xtatilganda bajariladigan funksiyalar.
    """
    logger.info("Bot to'xtatilmoqda...")
    
    # Session yopish
    await bot.session.close()
    
    logger.info("Bot to'xtatildi.")


def register_routers(dp: Dispatcher) -> None:
    """
    Barcha routerlarni ro'yxatdan o'tkazadi.
    
    Args:
        dp: Dispatcher obyekti
    """
    # Start va help handlerlari
    dp.include_router(start_router)
    
    # Media handler (asosiy)
    dp.include_router(media_router)
    
    logger.info("Barcha handlerlar ro'yxatdan o'tkazildi.")


async def main() -> None:
    """
    Botni ishga tushirish.
    """
    # Bot obyektini yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    # Dispatcher yaratish
    dp = Dispatcher()
    
    # Startup va shutdown handlerlari
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Routerlarni ro'yxatdan o'tkazish
    register_routers(dp)
    
    # Polling boshlash
    logger.info("Polling boshlandi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi (KeyboardInterrupt)")
    except Exception as e:
        logger.critical(f"Bot ishlashida kritikal xatolik: {e}", exc_info=True)