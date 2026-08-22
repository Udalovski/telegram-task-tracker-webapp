from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
import pytz

from app.config import settings
from app.database.models import User, Task, DayReport
from app.services.translator import translate_to_polish, format_daily_report_message


def get_user_current_date(user_timezone: str = "Europe/Warsaw") -> date:
    """Get current date in the user's timezone."""
    try:
        tz = pytz.timezone(user_timezone)
    except Exception:
        tz = pytz.timezone("Europe/Warsaw")
    return datetime.now(tz).date()


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None
) -> User:
    """Retrieve existing user or create a new one."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            timezone=settings.TIMEZONE,
            report_time=settings.DAILY_REPORT_TIME,
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:

        changed = False
        if username and user.username != username:
            user.username = username
            changed = True
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            changed = True
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            changed = True
        if changed:
            await session.commit()
            await session.refresh(user)

    return user


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_all_active_users(session: AsyncSession) -> List[User]:
    stmt = select(User).where(User.is_active == True)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def add_task(
    session: AsyncSession,
    user_id: int,
    raw_text: str,
    polish_text: Optional[str] = None,
    task_date: Optional[date] = None,
    source: str = "telegram_chat"
) -> Task:
    """Add a new task with automatic Polish translation if not provided."""
    if not polish_text:
        polish_text = await translate_to_polish(raw_text)

    if not task_date:
        task_date = date.today()

    task = Task(
        user_id=user_id,
        task_date=task_date,
        raw_text=raw_text.strip(),
        polish_text=polish_text.strip(),
        source=source,
        is_completed=True,
        is_deleted=False
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_today_tasks(
    session: AsyncSession,
    user_id: int,
    target_date: Optional[date] = None
) -> List[Task]:
    """Get all non-deleted tasks for a specific date (ordered by creation time)."""
    if not target_date:
        target_date = date.today()

    stmt = (
        select(Task)
        .where(
            and_(
                Task.user_id == user_id,
                Task.task_date == target_date,
                Task.is_deleted == False
            )
        )
        .order_by(Task.created_at.asc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_task_by_id(session: AsyncSession, task_id: int) -> Optional[Task]:
    stmt = select(Task).where(and_(Task.id == task_id, Task.is_deleted == False))
    result = await session.execute(stmt)
    return result.scalars().first()


async def update_task(
    session: AsyncSession,
    task_id: int,
    raw_text: Optional[str] = None,
    polish_text: Optional[str] = None
) -> Optional[Task]:
    """Update task raw text and/or Polish translation."""
    task = await get_task_by_id(session, task_id)
    if not task:
        return None

    if raw_text is not None:
        task.raw_text = raw_text.strip()

        if polish_text is None:
            task.polish_text = await translate_to_polish(raw_text)

    if polish_text is not None:
        task.polish_text = polish_text.strip()

    task.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task_id: int) -> bool:
    """Soft delete a task."""
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    task = result.scalars().first()
    if not task:
        return False

    task.is_deleted = True
    task.updated_at = datetime.utcnow()
    await session.commit()
    return True


async def get_history_last_7_days(
    session: AsyncSession,
    user_id: int,
    user_timezone: str = "Europe/Warsaw"
) -> List[Dict[str, Any]]:
    """
    Get tasks for the last 7 distinct days where tasks were logged.
    Grouped by date, sorted descending (newest first).
    """

    stmt = (
        select(Task)
        .where(
            and_(
                Task.user_id == user_id,
                Task.is_deleted == False
            )
        )
        .order_by(desc(Task.task_date), Task.created_at.asc())
    )
    result = await session.execute(stmt)
    all_tasks = result.scalars().all()


    grouped: Dict[date, List[Task]] = {}
    for task in all_tasks:
        if task.task_date not in grouped:
            grouped[task.task_date] = []
        grouped[task.task_date].append(task)


    sorted_dates = sorted(grouped.keys(), reverse=True)[:7]

    history_list = []
    for d in sorted_dates:
        day_tasks = grouped[d]
        tasks_data = [t.to_dict(user_timezone) for t in day_tasks]
        formatted_report = format_daily_report_message(d.strftime("%d.%m.%Y"), tasks_data)
        history_list.append({
            "date": d.isoformat(),
            "formatted_date": d.strftime("%d.%m.%Y"),
            "day_name": d.strftime("%A"),
            "task_count": len(tasks_data),
            "tasks": tasks_data,
            "report_preview": formatted_report
        })

    return history_list


async def save_or_update_day_report(
    session: AsyncSession,
    user_id: int,
    report_date: date,
    formatted_report: str,
    task_count: int,
    sent_at: Optional[datetime] = None
) -> DayReport:
    stmt = select(DayReport).where(
        and_(DayReport.user_id == user_id, DayReport.report_date == report_date)
    )
    result = await session.execute(stmt)
    report = result.scalars().first()

    if not report:
        report = DayReport(
            user_id=user_id,
            report_date=report_date,
            formatted_report=formatted_report,
            task_count=task_count,
            sent_at=sent_at
        )
        session.add(report)
    else:
        report.formatted_report = formatted_report
        report.task_count = task_count
        if sent_at:
            report.sent_at = sent_at

    await session.commit()
    await session.refresh(report)
    return report
