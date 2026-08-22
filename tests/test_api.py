import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import httpx
from main import app
from app.database.db import init_db


async def test_api_endpoints():
    print("Testing FastAPI Endpoints...")
    await init_db()

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:

        res = await client.get("/")
        assert res.status_code == 200, "HTML should be returned"
        assert "<title>Test Task Test Task | Raport Dzienny</title>" in res.text
        print("  ✅ GET / (Mini App HTML) returned 200 OK")


        res = await client.get("/api/user/profile?telegram_id=999999999")
        assert res.status_code == 200
        data = res.json()
        print(f"  ✅ GET /api/user/profile -> Report time: {data['report_time']}, TZ: {data['timezone']}")


        res = await client.get("/api/tasks/today?telegram_id=999999999")
        assert res.status_code == 200
        data = res.json()
        print(f"  ✅ GET /api/tasks/today -> {data['task_count']} tasks found")


        res = await client.post("/api/tasks?telegram_id=999999999", json={
            "raw_text": "Test Task Test Task Test Task"
        })
        assert res.status_code == 200
        created = res.json()["task"]
        print(f"  ✅ POST /api/tasks -> Created task #{created['id']}: {created['polish_text']}")


        res = await client.post("/api/tasks/translate", json={"text": "Test Task Test Task"})
        assert res.status_code == 200
        translated = res.json()["translated"]
        print(f"  ✅ POST /api/tasks/translate -> 'Test Task Test Task' = '{translated}'")


        res = await client.get("/api/tasks/history?telegram_id=999999999")
        assert res.status_code == 200
        history = res.json()["history"]
        print(f"  ✅ GET /api/tasks/history -> {len(history)} active days")

    print("\n🎉 ALL API ENDPOINTS OPERATING NORMALLY!")


if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
