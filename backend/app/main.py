"""FastAPI backend untuk Space Fighter."""

import base64
import hashlib
import hmac
import os
import re
import secrets
import time
from datetime import date
from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, get_db, init_db
from .game_logic import daily_seed, validate_run
from .security import hash_password, verify_password

app = FastAPI(title="Space Fighter API", version="1.0.0")

# Saat di-deploy, frontend dan API bisa satu origin. FRONTEND_ORIGIN dipakai
# hanya jika frontend di-host di domain berbeda. Default:* untuk kemudahan dev.
_origins = [o.strip() for o in os.getenv("FRONTEND_ORIGIN", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SEED_ITEMS = [
    {
        "code": "shield",
        "name": "Pelindung Ekstra",
        "description": "Menambah 1 nyawa di awal permainan.",
        "price": 150,
    },
    {
        "code": "rapid",
        "name": "Rapid Fire",
        "description": "Kecepatan tembak naik 40% selama satu run.",
        "price": 250,
    },
    # Pesawat premium: dibeli dari Shop, kepemilikan tercatat di inventory.
    {
        "code": "ship_spectre",
        "name": "SPECTRE (Pesawat)",
        "description": "Mata-mata kecil & sangat lincah, ukuran minimalis.",
        "price": 600,
    },
    {
        "code": "ship_nova",
        "name": "NOVA (Pesawat)",
        "description": "Interceptor sayap lebar dengan inti bercahaya.",
        "price": 1000,
    },
    {
        "code": "ship_titan",
        "name": "TITAN (Pesawat)",
        "description": "Kapaltempur besar, lambat tapi gagah.",
        "price": 1600,
    },
]

# Akun admin tunggal. Bisa diganti lewat environment variable tanpa edit kode.
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_DISPLAY_NAME = os.getenv("ADMIN_DISPLAY_NAME", "Administrator")
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "space-fighter-ubah-secret-ini")
ADMIN_TOKEN_TTL = 86400  # 24 jam


def make_admin_token(player_id: int) -> str:
    payload = f"{player_id}:{int(time.time()) + ADMIN_TOKEN_TTL}"
    signature = hmac.new(ADMIN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}:{signature}".encode()).decode()


def parse_admin_token(token: str):
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        player_id, expires, signature = raw.rsplit(":", 2)
        payload = f"{player_id}:{expires}"
        expected = hmac.new(ADMIN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        if int(expires) < int(time.time()):
            return None
        return int(player_id)
    except Exception:
        return None


def require_admin(
    x_admin_token: str = Header(...), db: Session = Depends(get_db)
) -> models.Player:
    """Semua endpoint admin harus membawa header X-Admin-Token."""
    player_id = parse_admin_token(x_admin_token)
    if not player_id:
        raise HTTPException(status_code=401, detail="Token admin tidak valid atau expired.")
    admin = (
        db.query(models.Player)
        .filter(models.Player.id == player_id, models.Player.is_admin.is_(True))
        .first()
    )
    if not admin:
        raise HTTPException(status_code=401, detail="Akses admin ditolak.")
    return admin


@app.on_event("startup")
def on_startup():
    init_db()
    db = SessionLocal()
    try:
        for data in SEED_ITEMS:
            if not db.query(models.Item).filter_by(code=data["code"]).first():
                db.add(models.Item(**data))

        # Pastikan hanya ada satu akun admin.
        others = (
            db.query(models.Player)
            .filter(
                models.Player.is_admin.is_(True),
                models.Player.username != ADMIN_USERNAME,
            )
            .all()
        )
        for other in others:
            other.is_admin = False

        admin = db.query(models.Player).filter_by(username=ADMIN_USERNAME).first()
        if not admin:
            db.add(
                models.Player(
                    username=ADMIN_USERNAME,
                    display_name=ADMIN_DISPLAY_NAME,
                    password_hash=hash_password(ADMIN_PASSWORD),
                    is_admin=True,
                )
            )
        else:
            admin.is_admin = True
            admin.password_hash = hash_password(ADMIN_PASSWORD)
        db.commit()
    finally:
        db.close()


def get_player_or_404(db: Session, player_id: int) -> models.Player:
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Pemain tidak ditemukan.")
    return player


# ---------- AUTH & PLAYER ----------

def normalize_email(value: str) -> str:
    return value.strip().lower()


def make_username(email: str) -> str:
    base = re.sub(r"[^a-z0-9_]", "", email.split("@")[0].lower())
    return (base[:44] or "pilot") + secrets.token_hex(2)


@app.post("/api/players/register", response_model=schemas.PlayerOut)
def register(payload: schemas.PlayerCreate, db: Session = Depends(get_db)):
    email = normalize_email(payload.email)
    if db.query(models.Player).filter(func.lower(models.Player.email) == email).first():
        raise HTTPException(status_code=400, detail="Email sudah terdaftar.")

    username = (payload.username or "").strip() or make_username(email)
    if db.query(models.Player).filter(func.lower(models.Player.username) == username.lower()).first():
        raise HTTPException(status_code=400, detail="Username sudah dipakai.")

    player = models.Player(
        username=username,
        email=email,
        display_name=payload.display_name.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@app.post("/api/players/login", response_model=schemas.PlayerOut)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    identifier = payload.identifier.strip().lower()
    player = db.query(models.Player).filter(
        or_(
            func.lower(models.Player.email) == identifier,
            func.lower(models.Player.username) == identifier,
        )
    ).first()
    if not player or not verify_password(payload.password, player.password_hash):
        raise HTTPException(status_code=401, detail="Email atau password salah.")
    return player


@app.get("/api/players/{player_id}", response_model=schemas.PlayerOut)
def get_player(player_id: int, db: Session = Depends(get_db)):
    return get_player_or_404(db, player_id)


# ---------- ITEM & INVENTORY ----------

@app.get("/api/items", response_model=List[schemas.ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()


@app.get("/api/players/{player_id}/inventory", response_model=List[schemas.InventoryOut])
def get_inventory(player_id: int, db: Session = Depends(get_db)):
    get_player_or_404(db, player_id)
    rows = (
        db.query(models.PlayerItem, models.Item)
        .join(models.Item, models.PlayerItem.item_code == models.Item.code)
        .filter(models.PlayerItem.player_id == player_id)
        .all()
    )
    return [
        schemas.InventoryOut(
            item_code=item.code, name=item.name, quantity=stock.quantity
        )
        for stock, item in rows
    ]


@app.post("/api/players/{player_id}/items/{item_code}/buy", response_model=schemas.MessageOut)
def buy_item(player_id: int, item_code: str, db: Session = Depends(get_db)):
    player = get_player_or_404(db, player_id)
    item = db.query(models.Item).filter_by(code=item_code).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan.")
    if player.coins < item.price:
        raise HTTPException(status_code=400, detail="Koin tidak cukup.")

    player.coins -= item.price
    stock = (
        db.query(models.PlayerItem)
        .filter_by(player_id=player_id, item_code=item_code)
        .first()
    )
    if stock:
        stock.quantity += 1
    else:
        db.add(
            models.PlayerItem(
                player_id=player_id, item_code=item_code, quantity=1
            )
        )
    db.commit()
    return {"message": f"Berhasil membeli {item.name}."}


# ---------- GAME SESSION ----------

@app.post("/api/games/start", response_model=schemas.SessionOut)
def start_game(payload: schemas.StartGameIn, db: Session = Depends(get_db)):
    player = get_player_or_404(db, payload.player_id)

    shield_active = False
    rapid_active = False
    for code in set(payload.equip):
        if code not in {"shield", "rapid"}:
            raise HTTPException(status_code=400, detail=f"Item {code} tidak dikenal.")
        stock = (
            db.query(models.PlayerItem)
            .filter_by(player_id=player.id, item_code=code)
            .first()
        )
        if not stock or stock.quantity < 1:
            raise HTTPException(status_code=400, detail=f"Item {code} tidak tersedia.")
        stock.quantity -= 1
        if code == "shield":
            shield_active = True
        if code == "rapid":
            rapid_active = True

    session = models.GameSession(
        player_id=player.id,
        seed=daily_seed(date.today().isoformat()),
        shield_active=shield_active,
        rapid_active=rapid_active,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@app.get("/api/games/{session_id}", response_model=schemas.SessionOut)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = (
        db.query(models.GameSession)
        .filter(models.GameSession.id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Sesi tidak ditemukan.")
    return session


@app.post("/api/games/{session_id}/finish", response_model=schemas.FinishOut)
def finish_game(
    session_id: int, payload: schemas.FinishIn, db: Session = Depends(get_db)
):
    session = (
        db.query(models.GameSession)
        .filter(models.GameSession.id == session_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Sesi tidak ditemukan.")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Sesi sudah selesai.")

    valid, reason = validate_run(
        payload.score,
        payload.wave,
        payload.enemies_killed,
        payload.duration_seconds,
        payload.max_combo,
    )

    session.score = payload.score
    session.wave = payload.wave
    session.enemies_killed = payload.enemies_killed
    session.max_combo = payload.max_combo
    session.duration_seconds = payload.duration_seconds
    session.status = "finished"

    coins_earned = 0
    rank = None
    if valid:
        player = get_player_or_404(db, session.player_id)
        coins_earned = payload.score // 100 + payload.wave * 5
        player.coins += coins_earned
        player.total_score += payload.score
        player.best_score = max(player.best_score, payload.score)

    db.add(
        models.Score(
            player_id=session.player_id,
            session_id=session.id,
            score=payload.score,
            wave=payload.wave,
            enemies_killed=payload.enemies_killed,
            max_combo=payload.max_combo,
            duration_seconds=payload.duration_seconds,
            validated=valid,
        )
    )
    db.commit()

    if valid:
        rank = (
            db.query(func.count(models.Score.id))
            .filter(models.Score.validated.is_(True), models.Score.score > payload.score)
            .scalar()
            + 1
        )

    return schemas.FinishOut(
        valid=valid,
        reason=reason,
        score=payload.score,
        rank=rank,
        coins_earned=coins_earned,
    )


# ---------- LEADERBOARD & HISTORY ----------

@app.get("/api/leaderboard", response_model=List[schemas.LeaderboardEntry])
def leaderboard(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    rows = (
        db.query(models.Score, models.Player)
        .join(models.Player, models.Score.player_id == models.Player.id)
        .filter(models.Score.validated.is_(True))
        .order_by(desc(models.Score.score), models.Score.created_at)
        .limit(limit)
        .all()
    )
    return [
        schemas.LeaderboardEntry(
            rank=index + 1,
            player_id=player.id,
            username=player.username,
            display_name=player.display_name,
            score=entry.score,
            wave=entry.wave,
            enemies_killed=entry.enemies_killed,
            created_at=entry.created_at,
        )
        for index, (entry, player) in enumerate(rows)
    ]


@app.get("/api/players/{player_id}/history", response_model=List[schemas.HistoryEntry])
def history(player_id: int, db: Session = Depends(get_db)):
    get_player_or_404(db, player_id)
    return (
        db.query(models.Score)
        .filter(models.Score.player_id == player_id)
        .order_by(desc(models.Score.created_at))
        .all()
    )


# ---------- ADMIN (khusus satu akun, butuh token) ----------

@app.post("/api/admin/login", response_model=schemas.AdminLoginOut)
def admin_login(payload: schemas.AdminLoginIn, db: Session = Depends(get_db)):
    admin = db.query(models.Player).filter_by(username=payload.username).first()
    if (
        not admin
        or not admin.is_admin
        or not verify_password(payload.password, admin.password_hash)
    ):
        raise HTTPException(status_code=401, detail="Kredensial admin salah.")
    return {"token": make_admin_token(admin.id), "admin": admin}


@app.get("/api/admin/stats", response_model=schemas.AdminStatsOut)
def admin_stats(
    admin: models.Player = Depends(require_admin), db: Session = Depends(get_db)
):
    scores = db.query(models.Score)
    return schemas.AdminStatsOut(
        players=db.query(func.count(models.Player.id)).scalar() or 0,
        finished_runs=scores.count(),
        valid_runs=scores.filter(models.Score.validated.is_(True)).count(),
        total_score=db.query(func.coalesce(func.sum(models.Score.score), 0))
        .filter(models.Score.validated.is_(True))
        .scalar()
        or 0,
        coins_in_circulation=db.query(func.coalesce(func.sum(models.Player.coins), 0)).scalar()
        or 0,
    )


@app.get("/api/admin/players", response_model=List[schemas.AdminPlayerOut])
def admin_players(
    admin: models.Player = Depends(require_admin), db: Session = Depends(get_db)
):
    return (
        db.query(models.Player)
        .order_by(desc(models.Player.best_score), models.Player.id)
        .all()
    )


@app.get("/api/admin/scores", response_model=List[schemas.AdminScoreOut])
def admin_scores(
    admin: models.Player = Depends(require_admin), db: Session = Depends(get_db)
):
    rows = (
        db.query(models.Score, models.Player)
        .join(models.Player, models.Score.player_id == models.Player.id)
        .order_by(desc(models.Score.created_at))
        .limit(200)
        .all()
    )
    return [
        schemas.AdminScoreOut(
            id=entry.id,
            player_id=player.id,
            username=player.username,
            display_name=player.display_name,
            score=entry.score,
            wave=entry.wave,
            enemies_killed=entry.enemies_killed,
            max_combo=entry.max_combo,
            duration_seconds=entry.duration_seconds,
            validated=entry.validated,
            created_at=entry.created_at,
        )
        for entry, player in rows
    ]


@app.get("/api/admin/sessions", response_model=List[schemas.AdminSessionOut])
def admin_sessions(
    admin: models.Player = Depends(require_admin), db: Session = Depends(get_db)
):
    rows = (
        db.query(models.GameSession, models.Player)
        .join(models.Player, models.GameSession.player_id == models.Player.id)
        .order_by(desc(models.GameSession.created_at))
        .limit(200)
        .all()
    )
    return [
        schemas.AdminSessionOut(
            id=session.id,
            player_id=player.id,
            username=player.username,
            status=session.status,
            seed=session.seed,
            score=session.score,
            wave=session.wave,
            enemies_killed=session.enemies_killed,
            duration_seconds=session.duration_seconds,
            created_at=session.created_at,
        )
        for session, player in rows
    ]


@app.get("/health")
def health():
    return {"status": "ok", "game": "Space Fighter"}


# Sajikan frontend dari satu URL yang sama dengan API.
# Mount ditaruh paling bawah supaya rute /api, /docs, dan /health tetap menang.
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend",
    )
