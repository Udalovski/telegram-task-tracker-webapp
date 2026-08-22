import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from app.database.db import async_session_maker
from app.services.task_service import (
    get_or_create_user,
    add_task,
    get_today_tasks,
    delete_task,
    get_user_current_date
)
from app.services.translator import format_daily_report_message
from app.bot.keyboards import (
    get_main_reply_keyboard,
    get_task_action_keyboard,
    get_report_action_keyboard
)
from app.config import settings

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command with friendly instructions."""
    async with async_session_maker() as session:
        user = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )

    if settings.WEBAPP_URL and settings.WEBAPP_URL.startswith("https://"):
        try:
            from aiogram.types import MenuButtonWebApp, WebAppInfo
            await message.bot.set_chat_menu_button(
                chat_id=message.chat.id,
                menu_button=MenuButtonWebApp(
                    text="Task",
                    web_app=WebAppInfo(url=settings.WEBAPP_URL)
                )
            )
        except Exception:
            pass

    welcome_text = (
        f"👋 Task, {message.from_user.first_name or 'Task'}!\n\n"
        "Task Task Task Task Task Task Task 🇵🇱\n\n"
        "✨ **Task Task Task:**\n"
        "1. Task Task Task Task Task Task Task Task, Task Task Task (Task: *\"Task Task\"*, *\"Task Task Task\"*).\n"
        "2. Task Task Task Task Task Task Task Task Task Task.\n"
        "3. **Task Task 20:00** (Task Task Task) Task Task Task Task Task Task Task.\n\n"
        "📱 **Mini App:** Task Task Task **\"Task Task\"** Task, Task Task Task Task, Task Task Task Task Task Task 7 Task!\n\n"
        "📋 Task /report Task /today — Task Task Task Task Task Task."
    )

    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_reply_keyboard()
    )


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Task")
async def cmd_help(message: Message):
    help_text = (
        "💡 **Task Task Task:**\n\n"
        "• **Task Task Task** — Task Task Task Task Task Task.\n"
        "• /report Task /today Task Task **📋 Task Task Task** — Task Task Task.\n"
        "• /app Task Task **📱 Task Task (Mini App)** — Task Task-Task (Task, Task, Task 7 Task).\n"
        f"• ⏰ **Task:** Task Task **{settings.DAILY_REPORT_TIME}** (Task / Warsaw).\n"
    )
    await message.answer(
        help_text,
        parse_mode="Markdown",
        reply_markup=get_main_reply_keyboard()
    )


@router.message(Command("today"))
@router.message(Command("report"))
@router.message(F.text == "📋 Task Task Task")
async def cmd_report(message: Message):
    """Generate and display today's report in Polish."""
    async with async_session_maker() as session:
        user = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        today_date = get_user_current_date(user.timezone)
        tasks = await get_today_tasks(session, user.id, today_date)

    if not tasks:
        await message.answer(
            f"ℹ️ Task Task ({today_date.strftime('%d.%m.%Y')}) Task Task Task Task.\n"
            "Task Task Task, Task Task Task Task!",
            reply_markup=get_main_reply_keyboard()
        )
        return

    tasks_data = [t.to_dict() for t in tasks]
    report_text = format_daily_report_message(
        today_date.strftime("%d.%m.%Y"),
        tasks_data,
        user_name=user.first_name or ""
    )

    await message.answer(
        report_text,
        parse_mode="Markdown",
        reply_markup=get_report_action_keyboard()
    )


@router.message(Command("app"))
async def cmd_app(message: Message):
    """Provide quick button to open Mini App."""
    await message.answer(
        "📱 Task Task Task Task Task:",
        reply_markup=get_main_reply_keyboard()
    )


@router.callback_query(F.data.startswith("del_task:"))
async def callback_delete_task(callback: CallbackQuery):
    """Handle instant delete button on task message."""
    task_id_str = callback.data.split(":")[1]
    try:
        task_id = int(task_id_str)
    except ValueError:
        await callback.answer("Task Task Task", show_alert=True)
        return

    async with async_session_maker() as session:
        success = await delete_task(session, task_id)

    if success:
        await callback.answer("🗑️ Task Task!")
        try:
            current_text = callback.message.text or ""
            await callback.message.edit_text(
                f"~~{current_text}~~\n\n_(Task Task)_",
                parse_mode="Markdown",
                reply_markup=None
            )
        except Exception:
            pass
    else:
        await callback.answer("Task Task Task Task Task Task.", show_alert=True)


@router.callback_query(F.data == "refresh_report")
async def callback_refresh_report(callback: CallbackQuery):
    """Refresh the daily report message."""
    async with async_session_maker() as session:
        user = await get_or_create_user(
            session,
            telegram_id=callback.from_user.id
        )
        today_date = get_user_current_date(user.timezone)
        tasks = await get_today_tasks(session, user.id, today_date)

    tasks_data = [t.to_dict() for t in tasks]
    report_text = format_daily_report_message(
        today_date.strftime("%d.%m.%Y"),
        tasks_data,
        user_name=user.first_name or ""
    )

    try:
        await callback.message.edit_text(
            report_text,
            parse_mode="Markdown",
            reply_markup=get_report_action_keyboard()
        )
        await callback.answer("🔄 Task Task!")
    except Exception:
        await callback.answer("Task Task Task.")


@router.message(F.text & ~F.text.startswith("/"))
async def handle_task_text(message: Message):
    """Receive task text, translate to Polish, store and acknowledge."""
    raw_text = message.text.strip()
    if not raw_text:
        return

    if raw_text in ["📱 Task Task (Mini App)", "📋 Task Task Task", "ℹ️ Task"]:
        return

    async with async_session_maker() as session:
        user = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )

        today_date = get_user_current_date(user.timezone)
        task = await add_task(
            session=session,
            user_id=user.id,
            raw_text=raw_text,
            task_date=today_date,
            source="telegram_chat"
        )
        
        today_tasks = await get_today_tasks(session, user.id, today_date)
        count = len(today_tasks)

    from app.database.models import format_local_time
    time_str = format_local_time(task.created_at, user.timezone)

    response_text = (
        f"✅ *Task:*\n"
        f"📝 {task.raw_text}\n"
        f"🇵🇱 *{task.polish_text}*\n\n"
        f"⏰ {time_str} | Task Task Task: *{count}*"
    )

    await message.reply(
        response_text,
        parse_mode="Markdown",
        reply_markup=get_task_action_keyboard(task.id)
    )