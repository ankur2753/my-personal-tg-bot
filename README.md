# `my-personal-tg-bot` — Universal Multi-Agent Telegram Control Gateway

> **Centralized, agent-agnostic Telegram control center and pub-sub message broker.**

---

## 🌟 Overview

`my-personal-tg-bot` acts as the master dispatch and response gateway for personal AI agents (e.g. `jobHunt`, future `finance-agent`, etc.). Rather than coupling Telegram directly to agent logic, `my-personal-tg-bot` uses a pluggable **Message Broker queue architecture** (Redis Streams / AWS SQS) for async, low-latency IPC.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- Docker & Docker Compose (for local Redis Streams)

### 2. Local Queue Infrastructure
Start the local Redis Streams container:
```bash
docker compose up -d
```

### 3. Environment Setup
Copy `.env.example` to `.env` and set your credentials:
```bash
cp .env.example .env
```

### 4. Install Dependencies & Run Tests
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest-asyncio
pytest
```

---

## 📖 Knowledge Base & Session Tracking

This repository follows a strict multi-session progress tracking system.
- Refer to [KNOWLEDGE_BASE.md](file:///home/ankurkumar/ankur_code/my-personal-tg-bot/KNOWLEDGE_BASE.md) for milestone requirements, active phase status, and session activity logs.
- Use the custom skill `tg-bot-kb` for session guidance.
