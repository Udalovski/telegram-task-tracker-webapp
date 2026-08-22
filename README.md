# 📋 Telegram Task & Habit Tracker with Integrated WebApp

> 🔒 **Confidentiality & Privacy Notice**: All UI texts, button labels, notifications, prompts, and application templates in this repository have been generalized and translated to English. Specific company data, proprietary workflows, internal links, and credentials have been replaced with generic open-source templates for privacy and compliance.

A modern, responsive productivity ecosystem featuring a **FastAPI** backend, **Telegram Bot** (`aiogram 3`), and a full-featured **Telegram Mini App (WebApp)** for managing daily tasks, tracking habits, and receiving automated daily performance digests.

---

## 🌟 Key Features

- **📱 Integrated Telegram WebApp (Mini App)**: Interactive web UI accessible directly within Telegram chat.
- **⚡ FastAPI Asynchronous Backend**: High-performance RESTful API endpoints for task CRUD, categorization, and statistics.
- **⏰ Automated Scheduled Digests**: Daily summary notifications and reminders sent at configurable times (`APScheduler`).
- **🗃️ Asynchronous Database**: Lightweight, zero-config local storage powered by **SQLite** + **aiosqlite**.
- **🤖 AI Task Assistant**: Optional natural language task decomposition and motivation using LLM integrations.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2
- **Telegram**: `aiogram 3.x`, Telegram WebApp API
- **Database**: SQLite, `aiosqlite`, SQLAlchemy
- **Scheduling**: `APScheduler`

---

## 🚀 Quick Start

1. **Clone repository:**
   ```bash
   git clone https://github.com/Udalovski/telegram-task-tracker-webapp.git
   cd telegram-task-tracker-webapp
   ```

2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure `.env`:**
   ```bash
   cp .env.example .env
   ```

4. **Start the application:**
   ```bash
   python main.py
   ```

---

## 📝 License
MIT License.
