"""Model SQLAlchemy ORM: Space Fighter."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


def now():
    return datetime.utcnow()


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=True, index=True)
    display_name = Column(String(80), nullable=False)
    password_hash = Column(String(255), nullable=False)
    coins = Column(Integer, default=0, nullable=False)
    total_score = Column(Integer, default=0, nullable=False)
    best_score = Column(Integer, default=0, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=now, nullable=False)

    sessions = relationship("GameSession", back_populates="player")
    scores = relationship("Score", back_populates="player")
    items = relationship("PlayerItem", back_populates="player")


class Item(Base):
    __tablename__ = "items"

    code = Column(String(30), primary_key=True)
    name = Column(String(60), nullable=False)
    description = Column(String(200), nullable=False)
    price = Column(Integer, nullable=False)


class PlayerItem(Base):
    __tablename__ = "player_items"

    player_id = Column(Integer, ForeignKey("players.id"), primary_key=True)
    item_code = Column(String(30), ForeignKey("items.code"), primary_key=True)
    quantity = Column(Integer, default=0, nullable=False)

    player = relationship("Player", back_populates="items")
    item = relationship("Item")


class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    seed = Column(Integer, nullable=False)
    status = Column(String(20), default="in_progress", nullable=False)
    shield_active = Column(Boolean, default=False, nullable=False)
    rapid_active = Column(Boolean, default=False, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    wave = Column(Integer, default=1, nullable=False)
    enemies_killed = Column(Integer, default=0, nullable=False)
    max_combo = Column(Integer, default=0, nullable=False)
    duration_seconds = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=now, nullable=False)
    finished_at = Column(DateTime, nullable=True)

    player = relationship("Player", back_populates="sessions")
    score_entry = relationship("Score", back_populates="session", uselist=False)

    @property
    def session_id(self) -> int:
        """Alias supaya response_model SessionOut bisa membaca id sesi."""
        return self.id


class Score(Base):
    """Satu baris = satu run selesai. Sumber leaderboard & riwayat."""

    __tablename__ = "scores"
    __table_args__ = (
        UniqueConstraint("session_id", name="uq_score_session"),
    )

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False)
    score = Column(Integer, nullable=False)
    wave = Column(Integer, nullable=False)
    enemies_killed = Column(Integer, nullable=False)
    max_combo = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    validated = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=now, nullable=False)

    player = relationship("Player", back_populates="scores")
    session = relationship("GameSession", back_populates="score_entry")
