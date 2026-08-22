import os
import asyncio
import logging
import uvicorn
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.db import init_db
from app.api.routes import router as api_router
from app.bot.bot import bot, dp, setup_bot_menu
from app.services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

bot_polling_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Initializing database...")
    await init_db()

    logger.info("Starting scheduler for daily reports (20:00 Warsaw time)...")
    start_scheduler()

    logger.info("Configuring Telegram bot menu...")
    await setup_bot_menu()


    global bot_polling_task
    logger.info("Starting Telegram bot polling...")
    bot_polling_task = asyncio.create_task(dp.start_polling(bot))

    yield


    logger.info("Shutting down scheduler...")
    stop_scheduler()

    if bot_polling_task:
        logger.info("Stopping Telegram bot...")
        bot_polling_task.cancel()
        try:
            await bot_polling_task
        except asyncio.CancelledError:
            pass

    await bot.session.close()
    logger.info("Application successfully stopped.")


app = FastAPI(
    title="Daily Work Reporter & Mini App",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)


web_dir = Path(__file__).resolve().parent / "app" / "web"
index_html_path = web_dir / "index.html"
style_css_path = web_dir / "style.css"
app_js_path = web_dir / "app.js"

app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


@app.api_route("/health", methods=["GET", "HEAD"])
@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health_check():
    """Healthcheck endpoint for monitoring / UptimeRobot / Render."""
    return {"status": "ok", "service": "Tasks Tracker Bot & WebApp"}


@app.api_route("/style.css", methods=["GET", "HEAD"])
async def serve_style():
    return FileResponse(str(style_css_path), media_type="text/css")


@app.api_route("/app.js", methods=["GET", "HEAD"])
async def serve_js():
    return FileResponse(str(app_js_path), media_type="application/javascript")


@app.api_route("/", methods=["GET", "HEAD"])
@app.api_route("/app", methods=["GET", "HEAD"])
@app.api_route("/webapp", methods=["GET", "HEAD"])
@app.api_route("/index.html", methods=["GET", "HEAD"])
async def serve_webapp():
    """Serve the Mini App Single Page Application."""
    if not index_html_path.exists():
        return JSONResponse(status_code=500, content={"error": f"index.html not found at {index_html_path}"})
    return FileResponse(str(index_html_path), media_type="text/html")


if __name__ == "__main__":
    port_env = os.environ.get("PORT")
    port = int(port_env) if port_env else settings.PORT
    host = os.environ.get("HOST", settings.HOST)
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=False)
