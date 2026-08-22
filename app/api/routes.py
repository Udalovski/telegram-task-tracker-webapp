from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.services.task_service import (
    get_or_create_user,
    add_task,
    get_today_tasks,
    get_task_by_id,
    update_task,
    delete_task,
    get_history_last_7_days,
    get_user_current_date,
    save_or_update_day_report
)
from app.services.translator import translate_to_polish, format_daily_report_message
from app.api.auth import get_current_telegram_user
from app.bot.bot import bot
from app.bot.keyboards import get_report_action_keyboard

router = APIRouter(prefix="/api", tags=["Mini App API"])


class CreateTaskRequest(BaseModel):
    raw_text: str
    polish_text: Optional[str] = None
    task_date: Optional[str] = None


class UpdateTaskRequest(BaseModel):
    raw_text: Optional[str] = None
    polish_text: Optional[str] = None


class TranslateRequest(BaseModel):
    text: str


class UpdateSettingsRequest(BaseModel):
    report_time: Optional[str] = None
    timezone: Optional[str] = None


@router.get("/user/profile")
async def get_user_profile(
    user_info: dict = Depends(get_current_telegram_user),
    session: AsyncSession = Depends(get_db)
):
    """Retrieve user details and settings."""
    user = await get_or_create_user(
        session=session,
        telegram_id=user_info["id"],
        username=user_info.get("username"),
        first_name=user_info.get("first_name"),
        last_name=user_info.get("last_name")
    )
    current_date = get_user_current_date(user.timezone)
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "first_name": user.first_name,
        "username": user.username,
        "timezone": user.timezone,
        "report_time": user.report_time,
        "current_date": current_date.isoformat(),
        "formatted_date": current_date.strftime("%d.%m.%Y")
    }


@router.put("/user/settings")
async def update_user_settings(
    req: UpdateSettingsRequest,
    user_info: dict = Depends(get_current_telegram_user),
    session: AsyncSession = Depends(get_db)
):
    """Update report notification time and timezone."""
    user = await get_or_create_user(
        session=session,
        telegram_id=user_info["id"]
    )
    if req.report_time:
        user.report_time = req.report_time
    if req.timezone:
        user.timezone = req.timezone

    await session.commit()
    await session.refresh(user)
    return {
        "success": True,
        "report_time": user.report_time,
        "timezone": user.timezone
    }


@router.get("/tasks/today")
async def get_tasks_today(
    user_info: dict = Depends(get_current_telegram_user),
    session: AsyncSession = Depends(get_db)
):
    """Get all today's tasks and the ready Polish daily report."""
    user = await get_or_create_user(
        session=session,
        telegram_id=user_info["id"],
        username=user_info.get("username"),
        first_name=user_info.get("first_name"),
        last_name=user_info.get("last_name")
    )
    today_date = get_user_current_date(user.timezone)
    tasks = await get_today_tasks(session, user.id, today_date)

    tasks_data = [t.to_dict(user.timezone) for t in tasks]
    report_text = format_daily_report_message(
        today_date.strftime("%d.%m.%Y"),
        tasks_data,
        user_name=user.first_name or ""
    )

    return {
        "date": today_date.isoformat(),
        "formatted_date": today_date.strftime("%d.%m.%Y"),
        "tasks": tasks_data,
        "task_count": len(tasks_data),
        "report_preview": report_text
    }


@router.post("/tasks")
async def create_new_task(
    req: CreateTaskRequest,
    user_info: dict = Depends(get_current_telegram_user),
    session: AsyncSession = Depends(get_db)
):
    """Add a new task from the Web App."""
    if not req.raw_text or not req.raw_text.strip():
        raise HTTPException(status_code=400, detail="Task text cannot be empty")

    user = await get_or_create_user(
        session=session,
        telegram_id=user_info["id"],
        username=user_info.get("username"),
        first_name=user_info.get("first_name"),
        last_name=user_info.get("last_name")
    )

    target_date = None
    if req.task_date:
        try:
            target_date = datetime.strptime(req.task_date, "%Y-%m-%d").date()
        except ValueError:
            target_date = get_user_current_date(user.timezone)
    else:
        target_date = get_user_current_date(user.timezone)

    task = await add_task(
        session=session,
        user_id=user.id,
        raw_text=req.raw_text,
        polish_text=req.polish_text,
        task_date=target_date,
        source="webapp"
    )

    return {"success": True, "task": task.to_dict(user.timezone)}


@router.put("/tasks/{task_id}")
async def edit_task(
    task_id: int,
    req: UpdateTaskRequest,
    user_info: dict = Depends(get_current_telegram_user),
    session: AsyncSession = Depends(get_db)
):
    """Edit an existing task's original text and/or Polish translation."""
    user = await get_or_create_user(session=session, telegram_id=user_info["id"])
    task = await get_task_by_id(session, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    updated = await update_task(
        session=session,
        task_id=task_id,
        raw_text=req.raw_text,
        polish_text=req.polish_text
    )

    return {"success": True, "task": updated.to_dict(user.timezone)}


@router.delete("/tasks/{task_id}")
async def remove_task(
    task_id: int,
    user_info: dict = Depends(get_current_telegram_user),
    session: AsyncSession = Depends(get_db)
):
    """Delete a task."""
    user = await get_or_create_user(session=session, telegram_id=user_info["id"])
    task = await get_task_by_id(session, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    await delete_task(session, task_id)
    return {"success": True, "message": "Task deleted"}


@router.get("/tasks/history")
async def get_task_history(
    user_info: dict = Depends(get_current_telegram_user),
    session: AsyncSession = Depends(get_db)
):
    """Get tasks grouped by date for the last 7 active days."""
    user = await get_or_create_user(session=session, telegram_id=user_info["id"])
    history = await get_history_last_7_days(session, user.id, user.timezone)
    return {"history": history}


@router.post("/tasks/translate")
async def live_translate(req: TranslateRequest):
    """Endpoint for live UI translation preview."""
    if not req.text or not req.text.strip():
        return {"translated": ""}
    translated = await translate_to_polish(req.text)
    return {"translated": translated}


@router.post("/report/send-now")
async def send_report_now(
    user_info: dict = Depends(get_current_telegram_user),
    session: AsyncSession = Depends(get_db)
):
    """Trigger sending today's report to the user's Telegram chat immediately."""
    user = await get_or_create_user(session=session, telegram_id=user_info["id"])
    today_date = get_user_current_date(user.timezone)
    tasks = await get_today_tasks(session, user.id, today_date)

    if not tasks:
        raise HTTPException(status_code=400, detail="Task error Task error Task error Task error Task error Task error Task error")

    tasks_data = [t.to_dict() for t in tasks]
    report_text = format_daily_report_message(
        today_date.strftime("%d.%m.%Y"),
        tasks_data,
        user_name=user.first_name or ""
    )

    header = "📋 *Task error Task error Task error (Task error Task error):* 🇵🇱\n\n"
    await bot.send_message(
        chat_id=user.telegram_id,
        text=header + report_text,
        parse_mode="Markdown",
        reply_markup=get_report_action_keyboard()
    )

    await save_or_update_day_report(
        session=session,
        user_id=user.id,
        report_date=today_date,
        formatted_report=report_text,
        task_count=len(tasks_data),
        sent_at=datetime.utcnow()
    )

    return {"success": True, "message": "Task error Task error Task error Task error Telegram!"}
