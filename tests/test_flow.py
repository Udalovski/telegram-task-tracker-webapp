import asyncio
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from app.database.db import init_db, async_session_maker
from app.services.translator import translate_to_polish, format_daily_report_message
from app.services.task_service import (
    get_or_create_user,
    add_task,
    get_today_tasks,
    update_task,
    delete_task,
    get_history_last_7_days
)
from datetime import date, timedelta


async def test_full_pipeline():
    print("=" * 60)
    print("1. Testing Database Initialization...")
    await init_db()
    print("✅ Database initialized successfully.")

    print("\n2. Testing Translation & Polish Formatting...")
    test_cases = [
        ("Test Task Test Task", "Umyto okna"),
        ("Test Task Test Task Test Task", "Inwentaryzacja"),
        ("Test Task Test Task", "Zrobiono / Sporządzono"),
        ("Test Task Test Task Test Task Test Task", "Odpowiedziano")
    ]
    for orig, expected_hint in test_cases:
        translated = await translate_to_polish(orig)
        print(f"  📝 '{orig}' ➡️ 🇵🇱 '{translated}'")
        assert len(translated) > 0, "Translation should not be empty"
    print("✅ Translation tests passed.")

    print("\n3. Testing Task Creation & Persistence...")
    async with async_session_maker() as session:

        user = await get_or_create_user(
            session=session,
            telegram_id=999999999,
            username="mariia_test",
            first_name="Test Task"
        )
        print(f"  User created: ID={user.id}, Name={user.first_name}")


        t1 = await add_task(session, user.id, "Test Task Test Task", task_date=date.today())
        t2 = await add_task(session, user.id, "Test Task Test Task Test Task", task_date=date.today())
        print(f"  Task 1: {t1.raw_text} -> {t1.polish_text}")
        print(f"  Task 2: {t2.raw_text} -> {t2.polish_text}")


        for d_offset in [1, 2, 3, 5]:
            past_date = date.today() - timedelta(days=d_offset)
            await add_task(
                session,
                user.id,
                f"Test Task Test Task Test Task {d_offset}",
                polish_text=f"Praca wykonana w dniu {d_offset}",
                task_date=past_date
            )


        today_tasks = await get_today_tasks(session, user.id, date.today())
        print(f"  Retrieved {len(today_tasks)} tasks for today.")
        assert len(today_tasks) >= 2, "Expected at least 2 tasks today"


        updated = await update_task(session, t1.id, raw_text="Test Task Test Task Test Task", polish_text="Umyto duże okna")
        print(f"  Updated task: {updated.polish_text}")
        assert updated.polish_text == "Umyto duże okna"


        history = await get_history_last_7_days(session, user.id)
        print(f"\n  Active days in history: {len(history)}")
        for day in history:
            print(f"   📅 {day['formatted_date']} ({day['day_name']}): {day['task_count']} tasks")
        assert len(history) >= 5, "Expected at least 5 active days in history"


        report = format_daily_report_message(date.today().strftime("%d.%m.%Y"), [t.to_dict() for t in today_tasks], user_name=user.first_name)
        print("\n4. Generated 20:00 Polish Report Preview:")
        print("-" * 40)
        print(report)
        print("-" * 40)
        assert "Raport dzienny" in report
        assert "Łącznie zadań" in report

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
