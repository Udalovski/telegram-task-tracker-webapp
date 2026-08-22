import logging
import pytz
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.database.db import async_session_maker
from app.database.models import User
from app.services.task_service import (
    get_all_active_users,
    get_today_tasks,
    save_or_update_day_report,
    get_user_current_date
)
from app.services.translator import format_daily_report_message
from app.bot.bot import bot
from app.bot.keyboards import get_report_action_keyboard

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def check_and_send_daily_reports():
    """
    Check active users and send 20:00 daily reports in their timezone.
    Called every minute or via scheduled cron.
    """
    now_utc = datetime.utcnow()

    async with async_session_maker() as session:
        users = await get_all_active_users(session)

        for user in users:
            try:
                user_tz = pytz.timezone(user.timezone or settings.TIMEZONE)
                user_now = datetime.now(user_tz)


                report_time_str = user.report_time or settings.DAILY_REPORT_TIME
                target_hour, target_minute = map(int, report_time_str.split(":"))


                if user_now.hour == target_hour and user_now.minute == target_minute:
                    today_date = user_now.date()
                    tasks = await get_today_tasks(session, user.id, today_date)

                    if not tasks:
                        logger.info(f"User {user.telegram_id} has no tasks for {today_date}, skipping report.")
                        continue

                    tasks_data = [t.to_dict() for t in tasks]
                    report_text = format_daily_report_message(
                        today_date.strftime("%d.%m.%Y"),
                        tasks_data,
                        user_name=user.first_name or ""
                    )


                    header_intro = "🔔 *Daily summary Daily summary Daily summary (20:00)!* 🇵🇱\nDaily summary Daily summary Daily summary Daily summary Daily summary Daily summary Daily summary:\n\n"
                    full_message = header_intro + report_text

                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=full_message,
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

                    logger.info(f"Successfully delivered 20:00 daily report to user {user.telegram_id} ({len(tasks_data)} tasks).")
            except Exception as e:
                logger.error(f"Failed to send scheduled report to user {user.telegram_id}: {e}")


def start_scheduler():
    """Start APScheduler to monitor and send daily reports every minute."""

    scheduler.add_job(
        check_and_send_daily_reports,
        trigger=CronTrigger(second=0),
        id="daily_report_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"Daily report scheduler started. Default report time: {settings.DAILY_REPORT_TIME} ({settings.TIMEZONE})")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Daily report scheduler stopped.")
