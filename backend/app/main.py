"""FastAPI backend untuk Space Fighter."""

from datetime import date
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, get_db, init_db
from .game_logic import daily_seed, validate_run
from .security import hash_password, verify_password

app = FastAPI(title="Space Fighter API", version="1.0.0")

# Frontend dijalankan dari file:// atau localhost, jadi CORS dibuka saat dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
]


@app.on_event("startup")
def on_startup():
    init_db()
    db = SessionLocal()
    try:
        for data in SEED_ITEMS:
            if not db.query(models.Item).filter_by(code=data["code"]).first():
                db.add(models.Item(**data))
        db.commit()
    finally:
        db.close()


def get_player_or_404(db: Session, player_id: int) -> models.Player:
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Pemain tidak ditemukan.")
    return player


# ---------- AUTH & PLAYER ----------

@app.post("/api/players/register", response_model=schemas.PlayerOut)
def register(payload: schemas.PlayerCreate, db: Session = Depends(get_db)):
    if db.query(models.Player).filter_by(username=payload.username).first():
        raise HTTPException(status_code=400, detail="Username sudah dipakai.")
    player = models.Player(
        username=payload.username,
        display_name=payload.display_name,
        password_hash=hash_password(payload.password),
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@app.post("/api/players/login", response_model=schemas.PlayerOut)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter_by(username=payload.username).first()
    if not player or not verify_password(payload.password, player.password_hash):
        raise HTTPException(status_code=401, detail="Username atau password salah.")
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


@app.get("/health")
def health():
    return {"status": "ok", "game": "Space Fighter"}
