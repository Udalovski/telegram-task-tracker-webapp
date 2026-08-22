import os
from pathlib import Path
from typing import AsyncGenerator
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings
from app.database.models import Base


raw_db_url = settings.DATABASE_URL.strip()

if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif raw_db_url.startswith("postgresql://") and not raw_db_url.startswith("postgresql+asyncpg://"):
    raw_db_url = raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)


if "asyncpg" in raw_db_url:
    parsed = urlparse(raw_db_url)
    query_params = parse_qs(parsed.query)

    needs_ssl = False
    if "sslmode" in query_params:
        val = query_params.pop("sslmode")[0]
        if val != "disable":
            needs_ssl = True
    if "ssl" in query_params:
        val = query_params.pop("ssl")[0]
        if val not in ("disable", "false"):
            needs_ssl = True
    if parsed.hostname and ("neon.tech" in parsed.hostname or "supabase.co" in parsed.hostname):
        needs_ssl = True


    unsupported_params = [
        "channel_binding",
        "gssencmode",
        "target_session_attrs",
        "endpoint",
        "options",
        "application_name"
    ]
    for p in unsupported_params:
        query_params.pop(p, None)

    if needs_ssl:
        query_params["ssl"] = ["require"]

    new_query = urlencode(query_params, doseq=True)
    db_url = urlunparse(parsed._replace(query=new_query))
else:
    db_url = raw_db_url

if db_url.startswith("sqlite+aiosqlite:///"):
    db_file_path = db_url.replace("sqlite+aiosqlite:///", "")
    Path(db_file_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(
    db_url,
    echo=False,
    future=True
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
