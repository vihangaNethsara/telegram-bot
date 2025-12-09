#!/usr/bin/env python3
"""
============================================
Society Payment Tracker Bot - Main Entry Point
============================================

Production-ready Telegram bot for tracking society
member payments with MySQL backend.

Author: Society Admin
Version: 1.0.0
License: MIT

Features:
- Telegram bot with polling mode
- MySQL database with connection pooling
- Payment recording and validation
- Admin commands and reports
- Excel export functionality
- Graceful shutdown handling

Usage:
    python main.py
"""

import os
import sys
import asyncio
import signal
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import after env is loaded
from config.db import init_db, close_db
from services.telegram_bot import create_application, set_bot_commands


def setup_logging() -> None:
    """Configure logging for the application."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler with rotation
            RotatingFileHandler(
                'logs/bot.log',
                maxBytes=5*1024*1024,  # 5 MB
                backupCount=5,
                encoding='utf-8'
            )
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")


def print_banner() -> None:
    """Print application banner."""
    print()
    print("=" * 48)
    print("  Society Payment Tracker Bot v1.0.0 (Python)")
    print("=" * 48)
    print()


async def main() -> None:
    """Main entry point for the application."""
    logger = logging.getLogger(__name__)
    application = None
    
    try:
        # Setup logging
        setup_logging()
        print_banner()
        
        # Initialize database
        logger.info("📦 Initializing database connection...")
        init_db()
        
        # Create bot application
        logger.info("🤖 Initializing Telegram bot...")
        application = create_application()
        
        # Initialize the application
        await application.initialize()
        
        # Set bot commands
        await set_bot_commands(application)
        
        # Print success message
        print()
        print("=" * 48)
        print("  🚀 Server started successfully!")
        print("=" * 48)
        print("  🤖 Telegram Bot: Running (Polling Mode)")
        print("  💾 Database: Connected")
        print("=" * 48)
        print()
        print("📝 Bot is now listening for messages...")
        print("   Send 'name-amount' to record payments")
        print("   Example: kamal-500")
        print()
        print("   Press Ctrl+C to stop the bot")
        print()
        
        # Start the bot with polling
        await application.start()
        await application.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=['message']
        )
        
        # Keep running until interrupted
        # Wait for a stop signal
        stop_event = asyncio.Event()
        
        # Handle shutdown signals
        def signal_handler():
            logger.info("⚠️ Shutdown signal received...")
            stop_event.set()
        
        # Register signal handlers (Unix only)
        if sys.platform != 'win32':
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, signal_handler)
        
        # Wait for stop signal
        try:
            # For Windows, we need to handle KeyboardInterrupt differently
            while not stop_event.is_set():
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("⚠️ Keyboard interrupt received...")
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        print()
        print("❌ Failed to start server:", str(e))
        print()
        print("Troubleshooting tips:")
        print("1. Check if MySQL server is running")
        print("2. Verify database credentials in .env file")
        print("3. Ensure BOT_TOKEN is valid")
        print("4. Check ADMIN_IDS are correct")
        print()
        sys.exit(1)
        
    finally:
        # Graceful shutdown
        print()
        logger.info("🛑 Starting graceful shutdown...")
        
        if application:
            try:
                # Stop the updater
                if application.updater and application.updater.running:
                    await application.updater.stop()
                    logger.info("🛑 Telegram bot polling stopped")
                
                # Stop the application
                await application.stop()
                await application.shutdown()
                logger.info("🛑 Telegram bot stopped")
            except Exception as e:
                logger.error(f"Error during bot shutdown: {e}")
        
        # Close database connections
        try:
            close_db()
        except Exception as e:
            logger.error(f"Error closing database: {e}")
        
        print()
        print("✅ Graceful shutdown completed")
        print()


if __name__ == '__main__':
    # Run the main async function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
