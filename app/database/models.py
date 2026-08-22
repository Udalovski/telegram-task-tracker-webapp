from datetime import datetime, date
import pytz
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    Date,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def format_local_time(dt: datetime, timezone_str: str = "Europe/Warsaw") -> str:
    """Format UTC datetime into user local time (HH:MM)."""
    if not dt:
        return ""
    try:
        tz = pytz.timezone(timezone_str or "Europe/Warsaw")
        if dt.tzinfo is None:
            utc_dt = pytz.utc.localize(dt)
        else:
            utc_dt = dt
        return utc_dt.astimezone(tz).strftime("%H:%M")
    except Exception:
        return dt.strftime("%H:%M")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    timezone = Column(String(64), default="Europe/Warsaw", nullable=False)
    report_time = Column(String(8), default="20:00", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("DayReport", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User telegram_id={self.telegram_id} name={self.first_name}>"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_date = Column(Date, default=date.today, nullable=False, index=True)
    raw_text = Column(Text, nullable=False)
    polish_text = Column(Text, nullable=False)
    source = Column(String(32), default="telegram_chat", nullable=False)
    is_completed = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="tasks")

    def to_dict(self, timezone_str: str = "Europe/Warsaw"):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "task_date": self.task_date.isoformat(),
            "raw_text": self.raw_text,
            "polish_text": self.polish_text,
            "source": self.source,
            "is_completed": self.is_completed,
            "is_deleted": self.is_deleted,
            "created_at": format_local_time(self.created_at, timezone_str),
            "created_at_iso": self.created_at.isoformat(),
            "updated_at_iso": self.updated_at.isoformat(),
        }


class DayReport(Base):
    __tablename__ = "day_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    report_date = Column(Date, default=date.today, nullable=False, index=True)
    formatted_report = Column(Text, nullable=False)
    task_count = Column(Integer, default=0, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="reports")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "report_date": self.report_date.isoformat(),
            "formatted_report": self.formatted_report,
            "task_count": self.task_count,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "created_at": self.created_at.isoformat(),
        }
