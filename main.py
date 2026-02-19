import app.db.base_class
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine
from app.api.v1.router import v1_router

# ----------------------------------------------
# CREATE APP
# ----------------------------------------------
app = FastAPI(title=settings.APP_NAME)
Instrumentator().instrument(app).expose(app)

# ----------------------------------------------
# REGISTER V1 ROUTER
# ----------------------------------------------
app.include_router(v1_router)

# ----------------------------------------------
# CORS
# ----------------------------------------------
origins = [
    "http://localhost:3000",  # Next.js dev
    # "https://yourdomain.com"  # Add in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------
# Startup DB
# ----------------------------------------------
@app.on_event("startup")
async def startup_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: None)

# ----------------------------------------------
# Health (outside v1 — infrastructure endpoint)
# ----------------------------------------------
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}