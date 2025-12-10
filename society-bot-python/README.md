# Society Payment Tracker Bot (Python) 🏛️🐍

A production-ready Telegram bot for tracking society member payments with MySQL backend. Built with Python, python-telegram-bot, and MySQL. Ready for deployment on Render.

## Features ✨

- **Payment Recording**: Members can record payments using simple `name-amount` format
- **Real-time Validation**: Validates name (letters only) and amount (positive numbers)
- **MySQL Database**: Persistent storage with connection pooling and SSL support
- **Cloud Ready**: Configured for Render deployment with cloud MySQL
- **Admin Commands**: View reports, export data, and manage records
- **Excel Export**: Export all payment data to styled Excel files
- **Daily/Monthly Reports**: Quick summaries of collections
- **Member History**: Track individual member payment history
- **Secure**: Admin-only commands protected by Telegram user IDs
- **Async Architecture**: Built with modern async/await patterns

## Tech Stack 🛠️

- **Runtime**: Python 3.11+
- **Telegram**: python-telegram-bot v21+
- **Database**: MySQL with mysql-connector-python
- **Hosting**: Render (Background Worker)
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
├── render.yaml                 # Render deployment config
├── Procfile                    # Worker process definition
├── runtime.txt                 # Python version
└── README.md                   # This file
```

## Prerequisites 📋

Before you begin, ensure you have:

1. **Python** 3.10 or higher installed
2. **SQL Server** (Express, Developer, or Standard) running locally
3. **ODBC Driver 17 for SQL Server** installed
4. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
5. **Your Telegram User ID** from [@userinfobot](https://t.me/userinfobot)

### Installing ODBC Driver 17 for SQL Server

Download and install from Microsoft:
- [ODBC Driver 17 for SQL Server - Windows](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

Or via PowerShell (Windows):
```powershell
# Check if driver is installed
Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}
```

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

Run these commands in SQL Server Management Studio (SSMS) or sqlcmd:

```sql
-- Create the database
CREATE DATABASE society_payments_db;
GO

USE society_payments_db;
GO

-- The table will be automatically created by the bot on first run
-- But you can create it manually if needed:
CREATE TABLE society_payments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    member_name NVARCHAR(100) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    recorded_by BIGINT NOT NULL,
    payment_date DATETIME DEFAULT GETDATE()
);

CREATE INDEX idx_member_name ON society_payments(member_name);
CREATE INDEX idx_payment_date ON society_payments(payment_date);
CREATE INDEX idx_recorded_by ON society_payments(recorded_by);
GO
```
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

# SQL Server Database Settings
# For Windows Authentication (leave DB_USER and DB_PASSWORD empty)
DB_SERVER=localhost
DB_NAME=society_payments_db
DB_USER=
DB_PASSWORD=
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUST_SERVER_CERTIFICATE=yes

# For SQL Server Authentication (provide username and password)
# DB_SERVER=localhost
# DB_NAME=society_payments_db
# DB_USER=sa
# DB_PASSWORD=your_password
# DB_DRIVER=ODBC Driver 17 for SQL Server
# DB_TRUST_SERVER_CERTIFICATE=yes

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

## Deploying to Render (FREE) 🚀

### Step 1: Set Up a Cloud MySQL Database

Since Render doesn't provide MySQL, you'll need an external MySQL provider:

**Recommended Free Options:**
- [PlanetScale](https://planetscale.com/) - Free tier with 5GB storage
- [Railway](https://railway.app/) - Free tier with MySQL
- [Aiven](https://aiven.io/) - Free trial available
- [TiDB Cloud](https://tidbcloud.com/) - Free tier available

Create a database and note down:
- Host
- Port (usually 3306)
- Username
- Password
- Database name

### Step 2: Push Code to GitHub

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 3: Deploy on Render (Free Web Service)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `society-payment-bot`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: **Free**

### Step 4: Set Environment Variables

In Render dashboard, add these environment variables:

| Variable | Value |
|----------|-------|
| `BOT_TOKEN` | Your Telegram bot token |
| `ADMIN_IDS` | Comma-separated admin user IDs |
| `DB_HOST` | Your MySQL host (e.g., `aws.connect.psdb.cloud`) |
| `DB_PORT` | `3306` |
| `DB_USER` | Your MySQL username |
| `DB_PASSWORD` | Your MySQL password |
| `DB_NAME` | Your database name |
| `DB_SSL` | `true` |
| `LOG_LEVEL` | `INFO` |

### Step 5: Deploy

Click **"Create Web Service"** and Render will:
1. Clone your repository
2. Install dependencies
3. Start your bot with a web server

### ⚠️ Important: Keep the Bot Alive

Render free tier spins down after 15 minutes of inactivity. To keep your bot running:

**Option 1: Use UptimeRobot (Recommended)**
1. Go to [UptimeRobot](https://uptimerobot.com/) (free)
2. Create a new monitor
3. Set type: **HTTP(s)**
4. URL: `https://your-app-name.onrender.com/health`
5. Interval: **5 minutes**

**Option 2: Use cron-job.org**
1. Go to [cron-job.org](https://cron-job.org/) (free)
2. Create a job to ping your `/health` endpoint every 5 minutes

This will keep your bot running 24/7 for free!

## Troubleshooting 🔧

### Bot Not Responding

1. Check if `BOT_TOKEN` is correct
2. Ensure the bot is added to your Telegram group
3. Check logs: `Get-Content .\logs\bot.log -Tail 50`

### Database Connection Failed

1. Verify SQL Server is running
2. Check database credentials in `.env`
3. Ensure database exists
4. Verify ODBC Driver 17 is installed: `Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}`
5. For Windows Auth, ensure your user has access to the database

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
After=network.target

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
