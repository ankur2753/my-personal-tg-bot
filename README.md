# `my-personal-tg-bot` — Universal Multi-Agent Telegram Control Gateway

> **Centralized, agent-agnostic Telegram control center and pub-sub message broker.**

---

## 🌟 Overview

`my-personal-tg-bot` acts as the master dispatch and response gateway for personal AI agents (e.g., [`jobHunt`](file:///home/ankurkumar/ankur_code/agent), future `finance-agent`, etc.). Rather than coupling Telegram directly to agent code, `my-personal-tg-bot` operates as a **Universal Message Router** over Redis Streams or AWS SQS.

```text
  [ Mobile / Desktop Telegram App ]
                 │
                 ▼
     [ my-personal-tg-bot ] ── (Security Guard & Intent Router)
                 │
  ┌──────────────┴──────────────┐
  ▼                             ▼
[ Queue: job-hunt.requests ]  [ Queue: finance.requests ]
  │                             │
  ▼                             ▼
[ Job Search Agent ]          [ Finance Agent ]
  │                             │
  └──────────────┬──────────────┘
                 ▼
[ Queue: agent.responses / notifications.global ] ──► Telegram Client
```

---

## 🚀 How to Setup and Run

### 1. Prerequisites
- **Python 3.10+** installed on your workstation.
- A **Telegram Bot Token** obtained from [@BotFather](https://t.me/BotFather) on Telegram.
- **Docker & Docker Compose** (Optional, for local zero-latency Redis Streams).

---

### 2. Environment & Dependency Setup

Clone the repository and set up a Python virtual environment:

```bash
# 1. Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install required packages
pip install -r requirements.txt
```

---

### 3. Configuration (`appsettings.json`)

Configuration is managed via `appsettings.json`. If `appsettings.json` does not exist, copy `appsettings.example.json`:

```bash
cp appsettings.example.json appsettings.json
```

Open `appsettings.json` in your code editor and configure your credentials:

```json
{
  "telegram": {
    "bot_token": "YOUR_BOTFATHER_TOKEN_HERE",
    "allowed_user_ids": [
      123456789,
      "shootingDragon",
      "@shootingDragon"
    ]
  },
  "queue": {
    "provider": "redis",
    "redis": {
      "host": "localhost",
      "port": 6379,
      "password": "secret_redis_pass",
      "db": 0
    },
    "aws_sqs": {
      "region": "us-east-1",
      "access_key_id": "",
      "secret_access_key": ""
    }
  },
  "google_sheets_webhook_url": "https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec",
  "topics": {
    "job_hunt_requests": "agent.job-hunt.requests",
    "job_hunt_responses": "agent.job-hunt.responses",
    "finance_requests": "agent.finance.requests",
    "finance_responses": "agent.finance.responses",
    "global_notifications": "notifications.global"
  }
}
```

#### 🔑 Configuration Breakdown:
| Parameter | Description |
| :--- | :--- |
| `telegram.bot_token` | **(Required)** Token provided by `@BotFather` when you create your bot. |
| `telegram.allowed_user_ids` | **(Required)** Whitelist array of numeric Telegram IDs or usernames (e.g. `"shootingDragon"`). Non-whitelisted accounts will be blocked. |
| `queue.provider` | Queue engine (`"redis"` for local Docker or `"aws_sqs"` for cloud). |
| `google_sheets_webhook_url` | **(Optional)** Google Apps Script URL to log resume creation results. |

> 🔒 **Security Note**: `appsettings.json` is listed in `.gitignore` and will never be pushed to Git.

---

### 4. Start the Queue Broker (Docker)

If using Redis Streams locally, start the Redis container:

```bash
docker compose up -d
```

*(If Docker is not running, `my-personal-tg-bot` will automatically operate in zero-dependency fallback mode for local testing).*

---

### 5. Run the Telegram Bot Gateway

Activate your virtual environment and start the bot service:

```bash
# Option A: Run using module syntax (Recommended)
.venv/bin/python -m src.main

# Option B: Run directly
source .venv/bin/activate
python src/main.py
```

Once started, open Telegram, search for your bot, and send:
- **`hi`**, **`hello`**, or **`/start`** — Displays the active capabilities menu (Tailored Resume Generator).
- **Paste any Job URL** (LinkedIn, Naukri, Company Careers page) — Automatically builds and queues a resume tailoring request envelope.
- **`/status`** — Displays system and broker connection health.

---

### 6. Run Test Suite Verification

Run the full pytest suite to verify interface contracts:

```bash
.venv/bin/pytest
```

---

### 📊 Google Sheets Logging Setup (Optional)

To automatically log resume creation events (`Result Time`, `Status`, `Company`, `Local Machine Filepath`) to a dedicated **`Resume Logs`** sheet tab in Google Sheets:

1. Open your Google Spreadsheet (https://sheets.google.com).
2. Click **Extensions** ➔ **Apps Script**.
3. Copy the contents of [`google_apps_script.js`](file:///home/ankurkumar/ankur_code/my-personal-tg-bot/google_apps_script.js) and paste into `Code.gs`.
4. Click **Deploy** ➔ **New deployment** ➔ Select type **Web app**.
5. Set *Execute as*: **Me**, *Who has access*: **Anyone**.
6. Click **Deploy**, copy the Web App URL, and paste into `google_sheets_webhook_url` in `appsettings.json`.

---

## 📖 Knowledge Base & Progress Tracking

This repository follows a strict multi-session progress tracking system.
- Refer to [KNOWLEDGE_BASE.md](file:///home/ankurkumar/ankur_code/my-personal-tg-bot/KNOWLEDGE_BASE.md) for phase requirements, milestone status matrix, and session activity logs.
- Use the custom skill `tg-bot-kb` for session initialization and finalization runbooks.
