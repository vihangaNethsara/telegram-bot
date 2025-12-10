#!/usr/bin/env python3
"""
============================================
Web App Entry Point for Render Free Tier
============================================

This module provides a Flask web server that:
1. Keeps the Render free web service alive
2. Runs the Telegram bot in the background

Render free tier requires a web service that
responds to HTTP requests to stay alive.
"""

import os
import sys
import asyncio
import threading
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import after env is loaded
from config.db import init_db, close_db
from services.telegram_bot import create_application, set_bot_commands

# Flask app
app = Flask(__name__)

# Global variables
bot_thread = None
bot_running = False


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
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")


def run_bot():
    """Run the Telegram bot in a separate thread."""
    global bot_running
    logger = logging.getLogger(__name__)
    
    async def start_bot():
        global bot_running
        application = None
        
        try:
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
            
            logger.info("🚀 Bot started successfully!")
            bot_running = True
            
            # Start the bot with polling
            await application.start()
            await application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=['message']
            )
            
            # Keep running
            while bot_running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
            bot_running = False
            
        finally:
            if application:
                try:
                    if application.updater and application.updater.running:
                        await application.updater.stop()
                    await application.stop()
                    await application.shutdown()
                except Exception as e:
                    logger.error(f"Error during shutdown: {e}")
            
            try:
                close_db()
            except Exception as e:
                logger.error(f"Error closing database: {e}")
    
    # Run the async bot
    asyncio.run(start_bot())


@app.route('/')
def home():
    """Health check endpoint."""
    return jsonify({
        'status': 'running',
        'service': 'Society Payment Tracker Bot',
        'bot_running': bot_running
    })


@app.route('/health')
def health():
    """Health check for Render."""
    return jsonify({'status': 'healthy', 'bot': 'running' if bot_running else 'starting'})


def start_bot_thread():
    """Start the bot in a background thread."""
    global bot_thread
    if bot_thread is None or not bot_thread.is_alive():
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logging.getLogger(__name__).info("🤖 Bot thread started")


# Setup logging and start bot when module loads
setup_logging()

print()
print("=" * 48)
print("  Society Payment Tracker Bot v1.0.0 (Render)")
print("=" * 48)
print()

# Start bot in background thread
start_bot_thread()

if __name__ == '__main__':
    # For local testing
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
