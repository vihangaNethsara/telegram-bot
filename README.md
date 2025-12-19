# Society Payment Tracker Bot 🤖

A production-ready Telegram bot for tracking society member payments with MySQL backend support.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Commands](#commands)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- 💰 **Payment Recording**: Record member payments with simple `name-amount` format
- 📊 **Payment Reports**: View last 20 payments, daily totals, and monthly summaries
- 👤 **Member History**: Track payment history for individual members
- 📈 **Statistics Dashboard**: Get comprehensive payment statistics
- 📥 **Excel Export**: Export payment data to formatted Excel spreadsheets
- 🔐 **Admin Controls**: Secure admin-only commands with role-based access
- 🗄️ **MySQL Backend**: Robust database with connection pooling
- 🔄 **Auto-recovery**: Graceful error handling and automatic reconnection
- 📝 **Logging**: Comprehensive logging with file rotation
- ☁️ **Cloud-Ready**: Optimized for deployment on Render, Heroku, and other platforms

## 🏗️ Architecture

```
┌─────────────┐
│  Telegram   │
│    Bot      │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Flask Web App  │  (Keeps service alive)
│   (Polling)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Controllers   │
│  (Business Logic)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MySQL Database │
│ (Connection Pool)│
└─────────────────┘
```

## 🔧 Prerequisites

- **Python**: 3.9 or higher
- **MySQL**: 5.7 or higher (or compatible cloud database)
- **Telegram Bot Token**: From [@BotFather](https://t.me/botfather)
- **pip**: Python package manager

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vihangaNethsara/telegram-bot.git
cd telegram-bot/society-bot-python
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `python-telegram-bot>=20.0` - Telegram Bot API wrapper
- `mysql-connector-python>=8.0` - MySQL database connector
- `python-dotenv>=1.0` - Environment variable management
- `flask>=3.0` - Web server for deployment
- `openpyxl>=3.1` - Excel file generation

### 3. Set Up MySQL Database

```sql
CREATE DATABASE society_payments_db;
USE society_payments_db;

CREATE TABLE society_payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_name VARCHAR(255) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    recorded_by BIGINT NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_member_name (member_name),
    INDEX idx_payment_date (payment_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `society-bot-python` directory:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321  # Comma-separated Telegram user IDs

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=society_payments_db
DB_SSL=false  # Set to 'true' for cloud databases

# Application Configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
PORT=10000  # For Render deployment
```

### Get Your Admin Telegram ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your user ID
3. Add it to `ADMIN_IDS` in `.env`

## 🚀 Usage

### Local Development

```bash
# Run the bot locally
python main.py
```

### Production (Render/Cloud)

```bash
# Run with web server (keeps service alive)
python app.py
```

### Recording Payments

Send a message in the format: `name-amount`

**Examples:**
```
kamal-500
Sarah-1000
john-250.50
```

**Response:**
```
✅ Payment Recorded

👤 Member: Kamal
💵 Amount: Rs. 500.00
🕐 Date: 2025-12-19 14:30
📝 Recorded by: John Admin
🆔 Payment ID: #42
```

## 📱 Commands

### User Commands

| Command | Description |
|---------|-------------|
| `/start` | Display welcome message and instructions |

### Admin Commands

| Command | Description |
|---------|-------------|
| `/table` | Show last 20 payment records |
| `/today` | Display today's total collection |
| `/month` | Show current month's summary |
| `/member <name>` | View payment history for a specific member |
| `/export` | Generate and download Excel report |
| `/stats` | Display comprehensive statistics |
| `/reset` | Clear all payment data (requires confirmation) |

### Command Examples

```
/table
/today
/month
/member kamal
/export
/stats
```

## 🌐 Deployment

### Render Deployment

1. **Create a Web Service** on [Render](https://render.com)

2. **Configure Build Settings:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

3. **Set Environment Variables:**
   - Add all variables from `.env` in Render dashboard
   - Set `DB_SSL=true` for cloud databases

4. **Choose Instance Type:**
   - Free tier works for small communities
   - Paid tier for better performance

### Heroku Deployment

```bash
# Install Heroku CLI and login
heroku login

# Create new app
heroku create your-app-name

# Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set ADMIN_IDS=your_ids
heroku config:set DB_HOST=your_db_host
# ... add all other variables

# Deploy
git push heroku main
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "app.py"]
```

## 📁 Project Structure

```
society-bot-python/
├── config/
│   ├── __init__.py
│   └── db.py                 # Database connection pool
├── controllers/
│   ├── __init__.py
│   └── payment_controller.py # Payment CRUD operations
├── routes/
│   ├── __init__.py
│   └── bot_routes.py         # Admin command handlers
├── services/
│   ├── __init__.py
│   └── telegram_bot.py       # Bot initialization & routing
├── logs/
│   └── bot.log              # Application logs (auto-created)
├── app.py                   # Web server entry point (production)
├── main.py                  # CLI entry point (development)
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (create this)
```

## 🔍 Key Components

### Database Layer (`config/db.py`)
- Connection pooling for efficient database access
- SSL support for cloud databases
- Automatic connection management
- Context managers for safe operations

### Controller Layer (`controllers/payment_controller.py`)
- Insert payments
- Query payment records
- Generate summaries and reports
- Data export functionality

### Service Layer (`services/telegram_bot.py`)
- Message parsing and validation
- Command routing
- Admin authentication
- Bot lifecycle management

### Routes Layer (`routes/bot_routes.py`)
- Admin command implementations
- Report generation
- Excel export
- Data management

## 🛠️ Development

### Running Tests

```bash
# Test database connection
python -c "from config.db import init_db; init_db()"

# Check bot configuration
python -c "from services.telegram_bot import load_admin_ids; load_admin_ids()"
```

### Logging

Logs are stored in `logs/bot.log` with automatic rotation:
- Maximum size: 5 MB per file
- Backup count: 5 files
- Format: `timestamp - logger - level - message`

View logs:
```bash
tail -f logs/bot.log
```

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit `.env` to version control
2. **Admin IDs**: Limit admin access to trusted users only
3. **Database**: Use strong passwords and SSL for production
4. **Bot Token**: Keep your Telegram bot token secret
5. **Input Validation**: All user inputs are sanitized
6. **SQL Injection**: Uses parameterized queries

## 📊 Database Schema

```sql
society_payments
├── id (INT, PRIMARY KEY, AUTO_INCREMENT)
├── member_name (VARCHAR(255), NOT NULL)
├── amount (DECIMAL(10,2), NOT NULL)
├── recorded_by (BIGINT, NOT NULL)
└── payment_date (DATETIME, DEFAULT CURRENT_TIMESTAMP)
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Vihanga Nethsara**
- GitHub: [@vihangaNethsara](https://github.com/vihangaNethsara)

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Excellent Telegram Bot API wrapper
- [MySQL Connector](https://dev.mysql.com/doc/connector-python/en/) - Reliable MySQL driver
- Community contributions and feedback

## 📞 Support

If you encounter any issues or have questions:
1. Check the logs in `logs/bot.log`
2. Review the [Issues](https://github.com/vihangaNethsara/telegram-bot/issues) page
3. Create a new issue with detailed information

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Payment categories
- [ ] Recurring payment reminders
- [ ] Advanced analytics dashboard
- [ ] Payment receipt generation
- [ ] Integration with payment gateways
- [ ] Mobile app companion

---

⭐ If you find this project helpful, please give it a star!