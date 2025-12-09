# Society Payment Tracker Bot (Python) 🏛️🐍

A production-ready Telegram bot for tracking society member payments with MySQL backend. Built with Python, python-telegram-bot, and MySQL.

## Features ✨

- **Payment Recording**: Members can record payments using simple `name-amount` format
- **Real-time Validation**: Validates name (letters only) and amount (positive numbers)
- **MySQL Database**: Persistent storage with connection pooling
- **Admin Commands**: View reports, export data, and manage records
- **Excel Export**: Export all payment data to styled Excel files
- **Daily/Monthly Reports**: Quick summaries of collections
- **Member History**: Track individual member payment history
- **Secure**: Admin-only commands protected by Telegram user IDs
- **Async Architecture**: Built with modern async/await patterns

## Tech Stack 🛠️

- **Runtime**: Python 3.10+
- **Telegram**: python-telegram-bot v21+
- **Database**: MySQL 8.0+ with mysql-connector-python
- **Excel Export**: openpyxl
- **Environment**: python-dotenv
- **Async**: asyncio (built-in)

## Project Structure 📁

```
society-bot-python/
├── config/
│   ├── __init__.py
│   └── db.py                   # Database connection pooling
├── controllers/
│   ├── __init__.py
│   └── payment_controller.py   # Database operations
├── routes/
│   ├── __init__.py
│   └── bot_routes.py           # Admin command handlers
├── services/
│   ├── __init__.py
│   └── telegram_bot.py         # Bot initialization & message handling
├── logs/                       # Log files (auto-created)
├── .env                        # Environment variables
├── .env.example                # Environment template
├── main.py                     # Main entry point
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Prerequisites 📋

Before you begin, ensure you have:

1. **Python** 3.10 or higher installed
2. **MySQL** 8.0+ server running
3. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
4. **Your Telegram User ID** from [@userinfobot](https://t.me/userinfobot)

## Installation 🚀

### Step 1: Navigate to the Project

```powershell
cd "c:\Users\vihanga nethsara\OneDrive\Desktop\telegram bot\society-bot-python"
```

### Step 2: Create Virtual Environment (Recommended)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Create the Database

Run these commands in MySQL:

```sql
CREATE DATABASE IF NOT EXISTS society_payments_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE society_payments_db;

CREATE TABLE IF NOT EXISTS society_payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_name VARCHAR(100) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    recorded_by BIGINT NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_member_name (member_name),
    INDEX idx_payment_date (payment_date),
    INDEX idx_recorded_by (recorded_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Step 5: Configure Environment Variables

Copy the example environment file:
```powershell
copy .env.example .env
```

Edit `.env` with your settings:
```env
# Telegram Bot Token (from @BotFather)
BOT_TOKEN=your_telegram_bot_token_here

# MySQL Database Settings
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=society_payments_db

# Admin Telegram User IDs (comma-separated)
ADMIN_IDS=123456789,987654321

# Logging Level
LOG_LEVEL=INFO
```

### Step 6: Start the Bot

```powershell
python main.py
```

## Usage 📱

### Recording Payments (Anyone)

Send a message in the format `name-amount`:

```
kamal-500
nimal-1000
sunil-750
```

The bot will respond:
```
✅ Payment recorded successfully
Member: Kamal
Amount: Rs.500.00
Date: 2024-01-15 14:30
```

### Admin Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Show available commands |
| `/table` | Show last 20 payments |
| `/today` | Today's total collection |
| `/month` | Current month's total |
| `/member <name>` | Member's payment history |
| `/export` | Export all data to Excel |
| `/stats` | Show payment statistics |
| `/reset` | Clear all records (requires confirmation) |

### Example Admin Interactions

**View Today's Collection:**
```
/today

📅 Today's Collection (2024-01-15)

💰 Total Amount: Rs.5,500.00
📝 Number of Payments: 8
```

**View Member History:**
```
/member kamal

👤 Payment History: Kamal

💰 Total Paid: Rs.2,500.00
📝 Total Payments: 5

Recent Payments:
• Rs.500.00 on 2024-01-15
• Rs.500.00 on 2024-01-10
...
```

## Validation Rules ✅

| Field | Rule |
|-------|------|
| Name | Letters only (a-z, A-Z) |
| Amount | Positive number |
| Format | Must contain exactly one `-` |

## Logging 📝

Logs are stored in the `logs/` directory with automatic rotation:
- Max file size: 5 MB
- Backup count: 5 files
- Encoding: UTF-8

Check logs for debugging:
```powershell
Get-Content .\logs\bot.log -Tail 50
```

## Security 🔒

- Admin commands are protected by Telegram user IDs
- Only users listed in `ADMIN_IDS` can run admin commands
- All payments store the `recorded_by` user ID for accountability
- Database uses parameterized queries to prevent SQL injection
- Connection pooling prevents resource exhaustion

## Differences from Node.js Version

| Feature | Node.js | Python |
|---------|---------|--------|
| Runtime | Node.js 18+ | Python 3.10+ |
| Telegram Library | node-telegram-bot-api | python-telegram-bot |
| DB Driver | mysql2 | mysql-connector-python |
| Excel Library | xlsx | openpyxl (with styles) |
| Async Pattern | Callbacks/Promises | async/await native |
| Logging | Console only | File + Console with rotation |

## Troubleshooting 🔧

### Bot Not Responding

1. Check if `BOT_TOKEN` is correct
2. Ensure the bot is added to your Telegram group
3. Check logs: `Get-Content .\logs\bot.log -Tail 50`

### Database Connection Failed

1. Verify MySQL is running
2. Check database credentials in `.env`
3. Ensure database exists

### ImportError for packages

Make sure virtual environment is activated:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Permission Denied for Commands

1. Verify your Telegram user ID is in `ADMIN_IDS`
2. Multiple IDs should be comma-separated

## Production Deployment 🚀

### Using systemd (Linux)

Create `/etc/systemd/system/society-bot.service`:

```ini
[Unit]
Description=Society Payment Tracker Bot
After=network.target mysql.service

[Service]
Type=simple
User=botuser
WorkingDirectory=/path/to/society-bot-python
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable society-bot
sudo systemctl start society-bot
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t society-bot .
docker run -d --env-file .env society-bot
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License.

---

Made with ❤️ and Python 🐍 for Society Payment Management
