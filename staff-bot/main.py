"""Staff Bot Service Entry Point."""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import settings
from handlers import start
from services.api_service import api_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_bot():
    """Run bot polling."""
    # Initialize bot and dispatcher
    bot = Bot(token=settings.STAFF_BOT_TOKEN)
    
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register routers
    dp.include_router(start.router)
    
    logger.info("Staff bot started and polling")
    
    try:
        # Start polling
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await api_service.close()
        await bot.session.close()


async def main():
    """Main function."""
    try:
        await run_bot()
    except Exception as e:
        logger.error(f"Error in staff bot: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())

