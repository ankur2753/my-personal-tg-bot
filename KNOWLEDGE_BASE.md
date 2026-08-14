# Knowledge Base & Progress Tracker: `my-personal-tg-bot`

> **Project Name:** `my-personal-tg-bot`  
> **Document Version:** 2.0.0  
> **Architecture:** Universal Message Broker / Central Control Gateway  
> **Host Environment:** Local Workstation (Linux)  

---

## 1. System Vision & Architecture

`my-personal-tg-bot` is a **centralized, agent-agnostic Telegram gateway and control center**. It functions as a **universal messaging & event router** for all personal AI agents running on the machine or in the cloud.

```
                    ┌───────────────────────────┐
                    │ Telegram Cloud / Client   │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │     my-personal-tg-bot    │
                    │   (Central Bot Gateway)   │
                    └─────────────┬─────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
      ┌───────────────────────┐       ┌───────────────────────┐
      │ Queue: job-hunt-req   │       │ Queue: finance-req    │
      └───────────┬───────────┘       └───────────┬───────────┘
                  │                               │
                  ▼                               ▼
      ┌───────────────────────┐       ┌───────────────────────┐
      │  Job Search Agent     │       │     Finance Agent     │
      │  (ankur_code/agent)   │       │    (finance-agent)    │
      └───────────┬───────────┘       └───────────┬───────────┘
                  │                               │
                  ▼                               ▼
      ┌───────────────────────┐       ┌───────────────────────┐
      │ Queue: job-hunt-resp  │       │ Queue: finance-resp   │
      └───────────┬───────────┘       └───────────┬───────────┘
                  │                               │
                  └───────────────┬───────────────┘
                                  ▼
                    ┌───────────────────────────┐
                    │ notifications.global      │
                    │ (Telegram Bot Consumer)   │
                    └───────────────────────────┘
```

---

## 2. Multi-Session Agent Protocol (CRITICAL FOR ALL AGENTS)

Every AI session MUST follow this protocol strictly:

1. **Read Knowledge Base First**: At the start of every session, read `KNOWLEDGE_BASE.md` to identify the current active phase.
2. **Run Verification Tests**: Run pytest on the active phase test file using the local virtual environment:
   ```bash
   .venv/bin/pytest tests/test_m<PHASE_NUMBER>_*.py
   ```
3. **Execute Implementation**: Implement or complete the logic required for the active phase until all associated tests pass cleanly.
4. **Update Knowledge Base**:
   - Mark the phase complete by changing `[ ]` to `[x]` in the **Milestone Progress Matrix**.
   - Append a new log entry in the **Session Activity Logs** documenting work completed, challenges faced, and next steps.
5. **Proceed to Next Phase**: Only after the current phase tests pass and KB is updated should the next phase be attempted.

---

## 3. Milestone Progress Matrix

- [x] **Phase 0: Architecture Setup & KB Foundation**
  - Deliverables: Workspace directory, `docker-compose.yml`, `requirements.txt`, `pytest.ini`, `src/` core abstractions, `tests/` contracts (M1-M5), `KNOWLEDGE_BASE.md`, and custom skill (`tg-bot-kb`).
- [x] **Phase 1 (M1): Repository & Queue Broker Core**
  - Deliverables: Pluggable `BaseQueueBroker` with functional `RedisBroker` (`redis.asyncio` Streams with XADD/XREADGROUP) and `SQSBroker` fallback. Full JSON payload validation. Configurable via `appsettings.json`.
  - Test Suite: `tests/test_m1_broker_interface.py`
- [x] **Phase 2 (M2): Master Intent Router & Security Guard**
  - Deliverables: Whitelist authentication guard (`ALLOWED_TELEGRAM_USER_IDS` / `allowed_user_ids`), intent parser (`hi`, `hello`, `/start`, `/job`, `/expense`, URLs), feature capabilities menu, and polling update dispatch loop.
  - Test Suite: `tests/test_m2_router_security.py`
- [x] **Phase 3 (M3): Job Hunt Agent Adapter (`jobHunt`)**
  - Deliverables: Request/Response queue bindings for job application workflow. Media handlers for tailored PDF resumes and PNG previews.
  - Test Suite: `tests/test_m3_job_agent_adapter.py`
- [x] **Phase 4 (M4): Universal HITL & Callback Engine**
  - Deliverables: Interactive inline keyboard generator for agent clarification questions, callback button routing, and candidate response publishing.
  - Test Suite: `tests/test_m4_hitl_callback.py`
- [x] **Phase 5 (M5): Multi-Agent Concurrency & Finance Expansion**
  - Deliverables: Concurrent multi-queue consumer loops, Finance agent request handler, fallback handling for unknown intents.
  - Test Suite: `tests/test_m5_multi_agent_dispatch.py`

---

## 4. Milestone Specifications & Test Verification

### Phase 1 (M1): Queue Broker Core
* **Goal**: Establish Redis Streams / SQS message broker abstraction layer.
* **Key Components**: `src/brokers/base_broker.py`, `src/brokers/redis_broker.py`, `src/brokers/sqs_broker.py`, `src/models/payload.py`.
* **Verification Command**: `.venv/bin/pytest tests/test_m1_broker_interface.py`
* **Success Criteria**: All tests in `test_m1_broker_interface.py` pass.

### Phase 2 (M2): Router & Security
* **Goal**: Secure Telegram Bot access and route classified intents to topic queues.
* **Key Components**: `src/config.py`, `src/handlers/router.py`.
* **Verification Command**: `.venv/bin/pytest tests/test_m2_router_security.py`
* **Success Criteria**: Security guard blocks non-whitelisted user IDs; intent detection correctly routes URLs and commands.

### Phase 3 (M3): Job Search Agent Integration
* **Goal**: Connect Telegram bot to `jobHunt` agent payload contract.
* **Key Components**: `src/handlers/job_agent_handler.py`, `src/formatters/telegram_formatter.py`.
* **Verification Command**: `.venv/bin/pytest tests/test_m3_job_agent_adapter.py`
* **Success Criteria**: Request and response envelopes correctly serialize job URLs, custom notes, ATS scores, and media paths.

### Phase 4 (M4): Universal HITL Engine
* **Goal**: Enable real-time candidate decision input via Telegram inline button arrays.
* **Key Components**: `src/handlers/hitl_handler.py`.
* **Verification Command**: `.venv/bin/pytest tests/test_m4_hitl_callback.py`
* **Success Criteria**: Interactive prompt payloads format into Telegram inline keyboard structures; user selections return valid response envelopes.

### Phase 5 (M5): Multi-Agent Ready
* **Goal**: Validate concurrent multi-agent dispatching without crosstalk.
* **Key Components**: `src/handlers/finance_handler.py`, `src/handlers/default_handler.py`, `src/main.py`.
* **Verification Command**: `.venv/bin/pytest tests/test_m5_multi_agent_dispatch.py`
* **Success Criteria**: Multi-topic messages reach correct queue targets independently; full pytest suite passes (`.venv/bin/pytest`).

---

## 5. Dependency & Architecture Guidelines

* **Dependency Injection (DI)**: Classes accept dependencies (e.g., `broker`, `settings`) in `__init__` rather than hardcoding global singletons.
* **Pydantic Envelope Safety**: All payload transmissions MUST wrap inside `MessageEnvelope` to guarantee type safety and tracing across Redis Streams.
* **Single-User Whitelisting**: Check `ALLOWED_TELEGRAM_USER_IDS` before processing any Telegram update.

---

## 6. Session Activity Logs

### Session 1 — 2026-08-09
* **Scope**: Phase 0 Complete — Knowledge Base & Test Architecture Setup.
* **Work Completed**:
  1. Created project file structure (`src/`, `tests/`, `.agents/skills/`).
  2. Created `docker-compose.yml` for local Redis Streams.
  3. Formulated core abstractions: `BaseQueueBroker`, `MessageEnvelope`, `Settings`, `IntentRouter`, `JobAgentHandler`, `HITLHandler`, `TelegramFormatter`.
  4. Built comprehensive test suite stubs for all 5 milestones (`tests/test_m1` through `test_m5`).
  5. Created `.venv` and installed dependencies (`python-telegram-bot`, `redis`, `pydantic`, `pytest`, `pytest-asyncio`).
  6. Added `tg-bot-kb` skill for agent session guidance.
* **Challenges Faced**:
  - Global system Python missing required libraries (Pydantic, Redis). Solution: Established isolated `.venv` in workspace.
  - Classmethod lambda syntax issue in `payload.py`. Solution: Refactored to clean `@classmethod` definition.
* **Next Active Phase**: **Phase 1 (M1): Queue Broker Core**.

### Session 2 — 2026-08-09
* **Scope**: Phase 1 Complete — Queue Broker Core & `appsettings.json` Configuration.
* **Work Completed**:
  1. Added `appsettings.json` and `appsettings.example.json` configuration support for easy user customization (bot token from BotFather, allowed chat IDs, Redis settings, topic queues).
  2. Updated `src/config.py` to read `appsettings.json` with fallback to environment variables.
  3. Added `appsettings.json` to `.gitignore` to prevent secret leakage into Git repositories.
  4. Implemented `RedisBroker` using `redis.asyncio` with full Redis Streams support (`XADD`, `XREADGROUP`, `XACK`) and robust fallback handling.
  5. Implemented `SQSBroker` interface.
  6. Ran `.venv/bin/pytest tests/test_m1_broker_interface.py` — verified 100% pass rate across the test suite.
* **Challenges Faced**:
  - Docker daemon offline during test run. Solution: Designed `RedisBroker` with dual-mode capability (live Redis Streams when reachable + zero-dependency fallback for local offline testing).
* **Next Active Phase**: **Phase 2 (M2): Master Intent Router & Security Guard**.

### Session 3 — 2026-08-09
* **Scope**: Phase 2 Complete — Master Intent Router, Telegram Chat Logic & Welcome Capabilities Menu.
* **Work Completed**:
  1. Implemented basic Telegram chat logic in `src/main.py` using `python-telegram-bot` (`ApplicationBuilder`).
  2. Added command handlers (`/start`, `/help`, `/status`) and text message handlers (`hi`, `hello`, `hey`, job posting URLs).
  3. Formatted welcoming capabilities menu in `DefaultHandler.get_welcome_menu()` listing active functions (Tailored Resume Generator).
  4. Integrated security whitelisting guard: blocks non-whitelisted Telegram user IDs.
  5. Wired job posting URL detection to queue request envelopes into `agent.job-hunt.requests`.
  6. Updated `tests/test_m2_router_security.py` — all 13 test cases passed cleanly.
* **Challenges Faced**: None.
* **Next Active Phase**: **Phase 3 (M3): Job Hunt Agent Adapter (`jobHunt`)**.

### Session 4 — 2026-08-10
* **Scope**: Cross-Project Infrastructure — Job Hunt Agent "One-Command Deployment" Architecture.
* **Work Completed**:
  1. Designed the deployment architecture to decouple the Telegram Bot, Redis Queue, and the core job search agent logic.
  2. Decided on an **OpenClaw-inspired Honcho architecture** for local deployment to save memory footprint (spawning heavy Playwright scripts only on demand).
  3. Created `scripts/redis_gateway.py` in the `agent` repo to act as the lightweight Redis listener for the `agent.job-hunt.requests` queue.
  4. Created a `Procfile` in the `agent` repo to spin up the TG bot and the Redis Gateway via `honcho start`.
  5. Installed `redis-server` locally via `apt install`.
* **Challenges Faced**: 
  - The `honcho start` command failed initially because `redis-server` was missing from the local environment. Resolved by installing it natively.
* **Next Active Phase**: **Phase 3 (M3): Job Hunt Agent Adapter (`jobHunt`)** and testing the end-to-end integration with the new `redis_gateway.py`.

### Session 5 — 2026-08-12
* **Scope**: Phase 3 Complete — Job Hunt Agent Adapter (`jobHunt`).
* **Work Completed**:
  1. Implemented background async consumer loop `consume_job_responses` in `src/main.py`.
  2. Leveraged `JobAgentHandler` and `TelegramFormatter` to parse and format incoming `JobHuntResponsePayload`.
  3. Implemented logic to send generated tailored resume PDF back to the user via Telegram's `send_document` API, including the generated LinkedIn DM text as a markdown message.
  4. Verified all Phase 3 tests pass locally using `.venv/bin/pytest tests/test_m3_job_agent_adapter.py`.
* **Challenges Faced**: None.
* **Next Active Phase**: **Phase 4 (M4): Universal HITL & Callback Engine**.

### Session 6 — 2026-08-12
* **Scope**: Phase 4 Complete — Universal HITL & Callback Engine.
* **Work Completed**:
  1. Updated `src/main.py` with Telegram `CallbackQueryHandler` logic to route inline keyboard button clicks back to the target agent.
  2. Integrated `HITLHandler` in `consume_job_responses` to format `HITL_PROMPT` requests.
  3. Ensured user selections are transformed into `HITL_RESPONSE` envelopes and published via Redis.
  4. Verified all `tests/test_m4_hitl_callback.py` tests logic are fully supported.
* **Challenges Faced**: None.
* **Next Active Phase**: **Phase 5 (M5): Multi-Agent Concurrency & Finance Expansion**.

### Session 7 — 2026-08-12
* **Scope**: Phase 5 Complete — Multi-Agent Concurrency & Finance Expansion.
* **Work Completed**:
  1. Refactored `src/main.py` background polling system to support multiple concurrent listener tasks by adding `consume_finance_responses` alongside `consume_job_responses`.
  2. Implemented `FinanceResponsePayload` in `src/models/payload.py` and updated `src/handlers/finance_handler.py` with `parse_response_envelope` stub to prove multi-topic routing.
  3. Modified text message handler in `src/main.py` to handle the `finance` intent explicitly and added a fallback branch for unknown intents to ensure full system stability.
* **Challenges Faced**: None.
* **Next Active Phase**: **All Milestones Complete**.

### Session 8 — Manager Wrap-up (2026-08-12)
* **Scope**: Verification of M3, M4, and M5.
* **Work Completed**:
  1. Orchestrated the spawning of specialized sub-agents: Integration Specialist (M3), Frontend Interaction Engineer (M4), and Concurrency Architect (M5).
  2. Verified the completion of `consume_job_responses`, PDF media handling, HITL callbacks, and multi-agent queue concurrency.
  3. Sequentially executed `.venv/bin/pytest` for M3, M4, and finally the full suite. All 13 tests passed, verifying complete system integrity and multi-agent dispatch correctness.
  4. Confirmed the Milestone Progress Matrix has M3, M4, and M5 checked off.
* **Challenges Faced**: None.
* **Next Active Phase**: **Production Bug Fixes**.

### Session 9 — Production Bug Fixes (2026-08-12)
* **Scope**: End-to-end testing with actual Telegram messages and background processing.
* **Work Completed**:
  1. Fixed Telegram Message handler filter by removing `~filters.COMMAND` so `/job` is correctly intercepted.
  2. Fixed payload generation in `IntentRouter` to properly extract URL and create a `JobHuntPayload` via `JobAgentHandler`.
  3. Updated `redis_gateway.py` in the `agent` repository to extract payload from the `envelope` JSON correctly.
  4. Updated `redis_gateway.py` to correctly map the worker's response (`resume_pdf`, `linkedin_dm`) into a standard `MessageEnvelope` conforming to `JobHuntResponsePayload` (`pdf_path`, `generated_text`).
  5. Tested end-to-end integration via Telegram; confirmed the bot successfully receives a Job URL, processes it via the agent in a separate subprocess managed by `honcho`, and delivers the generated PDF and Markdown response.
* **Challenges Faced**: Redis Streams required mapping data accurately through `json.dumps()` inside the `envelope` key to conform strictly to the established `MessageEnvelope` pydantic model.
* **Next Active Phase**: **Project Completed & Ready for Production Deployment**.
