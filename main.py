from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

from database.connection import engine, Base

# WAJIB import semua model supaya tabel dibuat
from models import user_model
from models import product_model
from models import order_model

# Routes
from routes import auth
from routes import product
from routes import order
from routes import auth, order


from core.logger import setup_logger

logger = setup_logger()

DB_FILE = "app.db"


# =========================
# LIFESPAN (Startup & Shutdown)
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting application...")

    # Cek file database
    if not os.path.exists(DB_FILE):
        logger.warning("⚠️ Database file not found. Creating new database...")
    else:
        logger.info("✅ Database file found.")

    # Buat tabel kalau belum ada
    Base.metadata.create_all(bind=engine)
    logger.info("🔥 Tables checked/created successfully")

    yield

    logger.warning("🛑 Application shutting down")


# =========================
# APP FACTORY
# =========================

def create_app() -> FastAPI:
    app = FastAPI(
        title="Digital Store API",
        version="1.0.0",
        lifespan=lifespan
    )

    # =========================
    # REQUEST LOGGER
    # =========================

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"➡️  {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"⬅️  Status: {response.status_code}")
        return response

    # =========================
    # CORS
    # =========================

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # =========================
    # ROUTERS
    # =========================

    app.include_router(auth.router)
    app.include_router(product.router)
    app.include_router(order.router)
    app.include_router(order.router)

    # =========================
    # ROOT ENDPOINT
    # =========================

    @app.get("/")
    def root():
        return {"status": "Server running"}

    return app


app = create_app()


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )