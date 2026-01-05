"""Bot Service Entry Point."""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import uvicorn

from bot.core.config import settings
from bot.handlers import start, menu, purchase, tickets, events, support, payment, music
from bot.handlers import catch_all
from bot.services.api_service import api_service
from bot.core.middleware import TemporaryMessagesMiddleware, temporary_messages_middleware
from bot.core.image_cache import preload_images
from bot.api_server import app as api_app, set_bot_instance

# Configure logging - always use DEBUG level for detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_bot():
    """Run bot polling."""
    # Preload all images into memory cache for fast access
    preload_images()
    
    # Initialize bot and dispatcher
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    set_bot_instance(bot)  # Set bot instance for API server
    
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
    dp.include_router(payment.router)
    dp.include_router(music.router)
    # Must be last: ensures every user message is "handled" so middleware runs
    dp.include_router(catch_all.router)
    
    logger.info("Bot started and polling")
    
    try:
        # Start polling
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await api_service.close()
        await bot.session.close()


async def main():
    """Main function - runs both HTTP server and bot polling."""
    # Start bot polling in background task
    bot_task = asyncio.create_task(run_bot())
    
    # Start FastAPI HTTP server
    config = uvicorn.Config(
        api_app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    try:
        logger.info("Starting bot with HTTP API server on port 8002")
        await server.serve()
    except Exception as e:
        logger.error(f"Error in HTTP server: {e}", exc_info=True)
    finally:
        # Cancel bot task
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
