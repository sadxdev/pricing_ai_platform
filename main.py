from fastapi import FastAPI
from app.core.config import settings
from app.db.session import engine

app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
async def startup_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: None)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}