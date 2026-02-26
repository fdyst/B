from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
import time

from database.connection import engine, Base

# WAJIB import semua model supaya tabel dibuat
from models import user_model
from models import product_model
from models import order_model
from models import wallet_model
from models import transaction_model
# IMPORT SEMUA MODEL DULU
from models.product_model import Product
from models.category_model import Category
from models.product_stock_model import ProductStock
# Routes
from routes import auth
from routes import product
from routes import order
from routes import user_web
from routes import user_pages
from routes import wallet_routes
from routes import admin_pages
from routes.category_routes import router as category_router

from core.logger import setup_logger

logger = setup_logger("main")

DB_FILE = "app.db"


# =========================
# LIFESPAN
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting application...")

    if not os.path.exists(DB_FILE):
        logger.warning("⚠️ Database file not found. Creating new database...")
    else:
        logger.info("✅ Database file found.")

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

    # Debug Request Logger Middleware
    @app.middleware("http")
    async def debug_middleware(request: Request, call_next):
        import uuid
        import traceback
        
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
    
        logger.info("\n" + "="*80)
        logger.info(f"🆔 Request ID: {request_id}")
        logger.info(f"📥 {request.method} {request.url}")
        logger.info(f"📍 Path: {request.url.path}")
        logger.info(f"🌍 Client: {request.client.host}:{request.client.port}")
    
        # Log headers penting
        logger.debug(f"Headers: Authorization={request.headers.get('authorization')}")
        logger.debug(f"Cookies: {request.cookies}")
    
        # Log body (kalau ada)
        try:
            body = await request.body()
            if body:
                logger.debug(f"Body: {body.decode(errors='ignore')}")
        except:
            logger.debug("Body: <unable to read>")
    
        try:
            response = await call_next(request)
            duration = time.time() - start_time
    
            logger.info(f"📤 Status: {response.status_code}")
            logger.info(f"⏱️ Duration: {duration:.4f}s")
            logger.info("="*80 + "\n")
    
            return response
    
        except Exception as e:
            duration = time.time() - start_time
    
            logger.error("🔥 UNHANDLED EXCEPTION")
            logger.error(f"🆔 Request ID: {request_id}")
            logger.error(f"Error Type: {type(e).__name__}")
            logger.error(f"Error Detail: {str(e)}")
            logger.error(f"⏱️ Duration: {duration:.4f}s")
            logger.error(traceback.format_exc())
            logger.error("="*80 + "\n")
    
            raise

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # STATIC FILES
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("✅ Static files mounted")
    except Exception as e:
        logger.warning(f"⚠️ Could not mount static files: {str(e)}")

    # ROUTERS
    logger.info("📚 Including routers...")
    app.include_router(auth.router)
    app.include_router(user_web.router)
    app.include_router(product.router)
    app.include_router(order.router)
    app.include_router(user_pages.router)
    app.include_router(wallet_routes.router)
    app.include_router(admin_pages.router)
    app.include_router(category_router)

    logger.info("✅ All routers included")

    @app.get("/")
    def root():
        logger.info("📍 Root endpoint accessed")
        return {"status": "Server running"}

    return app


app = create_app()


if __name__ == "__main__":
    logger.info("🎬 Starting FastAPI server...")
    logger.info(f"   Host: 0.0.0.0")
    logger.info(f"   Port: 8001")
    logger.info(f"   Reload: True")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )