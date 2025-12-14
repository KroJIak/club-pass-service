"""Bot Service Entry Point."""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.core.config import settings
from bot.handlers import start, menu, purchase, tickets, events, support
from bot.services.api_service import api_service
from bot.core.middleware import TemporaryMessagesMiddleware, temporary_messages_middleware

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main bot function."""
    # Initialize bot and dispatcher
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register middleware for temporary messages
    dp.message.middleware(temporary_messages_middleware)
    
    # Register routers
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(purchase.router)
    dp.include_router(tickets.router)
    dp.include_router(events.router)
    dp.include_router(support.router)
    
    logger.info("Bot started")
    
    try:
        # Start polling
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await api_service.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
