"""Skema request/response REST API."""

from datetime import datetime
from typing import List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class PlayerCreate(BaseModel):
    email: str = Field(min_length=5, max_length=120, pattern=EMAIL_PATTERN)
    display_name: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=4, max_length=100)
    # Username opsional; kalau kosong dibuat otomatis dari email.
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)


class LoginIn(BaseModel):
    # Bisa dikirim sebagai "identifier", "email", atau "username" (kompatibel lama).
    identifier: str = Field(validation_alias=AliasChoices("identifier", "email", "username"))
    password: str


class PlayerOut(ORMBase):
    id: int
    username: str
    email: Optional[str] = None
    display_name: str
    coins: int
    total_score: int
    best_score: int
    is_admin: bool = False
    created_at: datetime


class ItemOut(ORMBase):
    code: str
    name: str
    description: str
    price: int


class InventoryOut(BaseModel):
    item_code: str
    name: str
    quantity: int


class StartGameIn(BaseModel):
    player_id: int
    equip: List[str] = []  # item code yang dipakai: shield, rapid


class SessionOut(BaseModel):
    session_id: int
    seed: int
    status: str
    shield_active: bool
    rapid_active: bool
    wave: int


class FinishIn(BaseModel):
    score: int = Field(ge=0)
    wave: int = Field(ge=1)
    enemies_killed: int = Field(ge=0)
    max_combo: int = Field(ge=0)
    duration_seconds: int = Field(ge=0)


class FinishOut(BaseModel):
    valid: bool
    reason: str
    score: int
    rank: Optional[int] = None
    coins_earned: int = 0


class LeaderboardEntry(BaseModel):
    rank: int
    player_id: int
    username: str
    display_name: str
    score: int
    wave: int
    enemies_killed: int
    created_at: datetime


class HistoryEntry(BaseModel):
    session_id: int
    score: int
    wave: int
    enemies_killed: int
    max_combo: int
    duration_seconds: int
    validated: bool
    created_at: datetime


class MessageOut(BaseModel):
    message: str


# ---------- ADMIN ----------

class AdminLoginIn(BaseModel):
    username: str
    password: str


class AdminLoginOut(BaseModel):
    token: str
    admin: PlayerOut


class AdminPlayerOut(ORMBase):
    id: int
    username: str
    email: Optional[str] = None
    display_name: str
    coins: int
    total_score: int
    best_score: int
    is_admin: bool
    created_at: datetime


class AdminScoreOut(ORMBase):
    id: int
    player_id: int
    username: str
    display_name: str
    score: int
    wave: int
    enemies_killed: int
    max_combo: int
    duration_seconds: int
    validated: bool
    created_at: datetime


class AdminSessionOut(ORMBase):
    id: int
    player_id: int
    username: str
    status: str
    seed: int
    score: int
    wave: int
    enemies_killed: int
    duration_seconds: int
    created_at: datetime


class AdminStatsOut(BaseModel):
    players: int
    finished_runs: int
    valid_runs: int
    total_score: int
    coins_in_circulation: int
