"""
============================================
Telegram Bot Service - Core Bot Logic
============================================

This module initializes and manages the Telegram bot,
handling message parsing, validation, and routing.

Features:
- Bot initialization with polling mode
- Message format validation (name-amount)
- Payment recording
- Admin command routing
- Error handling
"""

import os
import re
import logging
from datetime import datetime
from typing import List, Set

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv

from controllers.payment_controller import payment_controller
from routes import bot_routes

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Admin user IDs from environment variable
ADMIN_IDS: Set[int] = set()


def load_admin_ids() -> None:
    """Load admin IDs from environment variable."""
    global ADMIN_IDS
    admin_ids_str = os.getenv('ADMIN_IDS', '')
    
    if admin_ids_str:
        try:
            ADMIN_IDS = {
                int(id_str.strip())
                for id_str in admin_ids_str.split(',')
                if id_str.strip().isdigit()
            }
        except ValueError as e:
            logger.error(f"Error parsing ADMIN_IDS: {e}")
            ADMIN_IDS = set()
    
    logger.info(f"👮 Admin IDs: {', '.join(map(str, ADMIN_IDS)) if ADMIN_IDS else 'None configured'}")


def is_admin(user_id: int) -> bool:
    """
    Check if a user is an admin.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user is an admin
    """
    return user_id in ADMIN_IDS


def is_valid_name(name: str) -> bool:
    """
    Validate member name (letters only).
    
    Args:
        name: Name to validate
        
    Returns:
        True if valid
    """
    if not name or len(name) == 0 or len(name) > 100:
        return False
    
    # Allow only letters (including Unicode letters for international names)
    pattern = r'^[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF]+$'
    return bool(re.match(pattern, name))


def is_valid_amount(amount_str: str) -> bool:
    """
    Validate payment amount string.
    
    Args:
        amount_str: Amount string to validate
        
    Returns:
        True if valid positive number
    """
    try:
        amount = float(amount_str)
        return 0 < amount <= 99999999.99
    except (ValueError, TypeError):
        return False


def capitalize_first_letter(text: str) -> str:
    """
    Capitalize first letter of a string.
    
    Args:
        text: String to capitalize
        
    Returns:
        Capitalized string
    """
    if not text:
        return text
    return text[0].upper() + text[1:].lower()


def format_datetime(dt: datetime) -> str:
    """
    Format date and time for display.
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted string (YYYY-MM-DD HH:MM)
    """
    return dt.strftime('%Y-%m-%d %H:%M')


# ============================================
# Command Handlers
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - Send welcome message."""
    chat_id = update.effective_chat.id
    
    message = (
        "🏛️ *Welcome to Society Payment Tracker Bot*\n\n"
        "This bot helps track member payments for the society.\n\n"
        "*How to record a payment:*\n"
        "Simply send a message in the format:\n"
        "`name-amount`\n\n"
        "*Examples:*\n"
        "• kamal-500\n"
        "• nimal-1000\n\n"
        "Type /help for more commands."
    )
    
    await context.bot.send_message(chat_id, message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - Send help message."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    message = (
        "📚 *Society Payment Tracker - Help*\n\n"
        "*Recording Payments:*\n"
        "Send a message in format: `name-amount`\n"
        "Example: `kamal-500`\n\n"
        "*Rules:*\n"
        "• Name must contain only letters\n"
        "• Amount must be a positive number\n"
    )
    
    if is_admin(user_id):
        message += (
            "\n*Admin Commands:*\n"
            "/table - Show last 20 payments\n"
            "/today - Show today's total collection\n"
            "/month - Show current month's total\n"
            "/member <name> - Show member's payment history\n"
            "/export - Export all data to Excel\n"
            "/stats - Show payment statistics\n"
            "/reset - Clear all records (confirmation required)\n"
        )
    
    await context.bot.send_message(chat_id, message, parse_mode='Markdown')


async def admin_only(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if user is admin and send unauthorized message if not.
    
    Returns:
        True if user is admin, False otherwise
    """
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await context.bot.send_message(
            update.effective_chat.id,
            '🔒 This command is only available to administrators.'
        )
        return False
    
    return True


async def table_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /table command - Admin only."""
    if await admin_only(update, context):
        await bot_routes.handle_table_command(update, context)


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /today command - Admin only."""
    if await admin_only(update, context):
        await bot_routes.handle_today_command(update, context)


async def month_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /month command - Admin only."""
    if await admin_only(update, context):
        await bot_routes.handle_month_command(update, context)


async def member_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /member command - Admin only."""
    if await admin_only(update, context):
        await bot_routes.handle_member_command(update, context)


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /export command - Admin only."""
    if await admin_only(update, context):
        await bot_routes.handle_export_command(update, context)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /reset command - Admin only."""
    if await admin_only(update, context):
        await bot_routes.handle_reset_command(update, context)


async def confirm_reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /confirm_reset command - Admin only."""
    if await admin_only(update, context):
        await bot_routes.handle_confirm_reset_command(update, context)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command - Admin only."""
    if await admin_only(update, context):
        await bot_routes.handle_stats_command(update, context)


# ============================================
# Message Handler
# ============================================

async def handle_payment_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle payment format messages (name-amount).
    
    Args:
        update: Telegram update object
        context: Callback context
    """
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or update.effective_user.username or 'Unknown'
    
    # Log incoming message
    logger.info(f"📩 Message from {user_name} ({user_id}): {text}")
    
    # Check if message contains hyphen
    if '-' not in text:
        return  # Ignore messages without hyphen
    
    # Parse the payment format: name-amount
    parts = text.split('-')
    
    # Must have exactly 2 parts
    if len(parts) != 2:
        await context.bot.send_message(
            chat_id,
            '❌ Invalid format. Use: name-amount (example: kamal-500)'
        )
        return
    
    name = parts[0].strip()
    amount_str = parts[1].strip()
    
    # Validate name
    if not is_valid_name(name):
        await context.bot.send_message(
            chat_id,
            '❌ Invalid format. Use: name-amount (example: kamal-500)'
        )
        return
    
    # Validate amount
    if not is_valid_amount(amount_str):
        await context.bot.send_message(
            chat_id,
            '❌ Invalid format. Use: name-amount (example: kamal-500)'
        )
        return
    
    amount = float(amount_str)
    
    try:
        # Insert payment into database
        payment = payment_controller.insert_payment(name, amount, user_id)
        
        # Format the date
        payment_date = payment['payment_date']
        formatted_date = format_datetime(payment_date)
        
        # Capitalize member name for display
        display_name = capitalize_first_letter(name)
        
        # Send success message
        success_message = (
            f"✅ Payment recorded successfully\n"
            f"Member: {display_name}\n"
            f"Amount: Rs.{amount:.2f}\n"
            f"Date: {formatted_date}"
        )
        
        await context.bot.send_message(chat_id, success_message)
        logger.info(f"✅ Payment recorded: {display_name} - Rs.{amount}")
        
    except Exception as e:
        logger.error(f"❌ Error recording payment: {e}")
        await context.bot.send_message(
            chat_id,
            '❌ Failed to record payment. Please try again.'
        )


# ============================================
# Error Handler
# ============================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error(f"❌ Exception while handling an update: {context.error}")
    
    if update and update.effective_chat:
        try:
            await context.bot.send_message(
                update.effective_chat.id,
                '❌ An error occurred while processing your request.'
            )
        except Exception as e:
            logger.error(f"❌ Could not send error message: {e}")


# ============================================
# Bot Initialization
# ============================================

def create_application() -> Application:
    """
    Create and configure the Telegram bot application.
    
    Returns:
        Configured Application instance
    """
    token = os.getenv('BOT_TOKEN')
    
    if not token:
        raise ValueError("BOT_TOKEN is not defined in environment variables")
    
    # Load admin IDs
    load_admin_ids()
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("table", table_command))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(CommandHandler("month", month_command))
    application.add_handler(CommandHandler("member", member_command))
    application.add_handler(CommandHandler("export", export_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("confirm_reset", confirm_reset_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Add message handler for payment messages
    # Only process text messages that are not commands
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_payment_message
    ))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    logger.info("🤖 Telegram bot application created")
    
    return application


async def set_bot_commands(application: Application) -> None:
    """Set bot commands in Telegram menu."""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help message"),
        BotCommand("table", "Show last 20 payments (Admin)"),
        BotCommand("today", "Show today's total (Admin)"),
        BotCommand("month", "Show monthly total (Admin)"),
        BotCommand("member", "Show member history (Admin)"),
        BotCommand("export", "Export to Excel (Admin)"),
        BotCommand("stats", "Show statistics (Admin)"),
        BotCommand("reset", "Reset all data (Admin)")
    ]
    
    await application.bot.set_my_commands(commands)
    logger.info("✅ Bot commands set successfully")
