---
name: tg-bot-kb
description: Knowledge Base and Session Progress Manager for my-personal-tg-bot. Use this skill at the start and end of any session to check active implementation phase, run milestone verification tests, and record progress.
---

# `my-personal-tg-bot` Knowledge Base & Session Manager

This skill governs the development lifecycle and session tracking for `my-personal-tg-bot`.

---

## 1. Session Initialization Runbook

Whenever starting or resuming work on this repository:

1. **Read the Knowledge Base**:
   Inspect [KNOWLEDGE_BASE.md](file:///home/ankurkumar/ankur_code/my-personal-tg-bot/KNOWLEDGE_BASE.md) to check:
   - What phases are marked `[x]` (completed) vs `[ ]` (pending).
   - What the active phase is and its requirements.
   - Recent notes and challenges in **Session Activity Logs**.

2. **Run Active Phase Verification Tests**:
   Execute pytest on the active phase test suite using the project virtual environment:
   ```bash
   .venv/bin/pytest tests/test_m<PHASE_NUMBER>_*.py
   ```

3. **Implement Phase Requirements**:
   Focus strictly on the active phase deliverables defined in `KNOWLEDGE_BASE.md` until all tests in the phase suite pass.

---

## 2. Session Handover & Finalization Runbook

Before completing a session or wrapping up work:

1. **Run Full Test Suite**:
   ```bash
   .venv/bin/pytest
   ```

2. **Update Check Marks**:
   If the phase test suite passes completely, mark the phase `[x]` in the **Milestone Progress Matrix** in [KNOWLEDGE_BASE.md](file:///home/ankurkumar/ankur_code/my-personal-tg-bot/KNOWLEDGE_BASE.md).

3. **Log Session Details**:
   Add an entry under **Session Activity Logs** in [KNOWLEDGE_BASE.md](file:///home/ankurkumar/ankur_code/my-personal-tg-bot/KNOWLEDGE_BASE.md):
   - **Scope**: Phase worked on
   - **Work Completed**: Key features implemented or refactored
   - **Challenges Faced**: Any issues, bugs, or key architectural decisions
   - **Next Active Phase**: Phase to be tackled in the next session
