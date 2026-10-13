from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import os

from app.config import settings
from app.database import init_db, seed_initial_data_if_empty
from app.routers import brand, knowledge, products, posts, content, research, performance, exports, system

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed products/brand if empty
    init_db()
    seed_initial_data_if_empty()
    yield

app = FastAPI(
    title=settings.app_name,
    description="Local-First LinkedIn B2B Growth & Sales Copilot with Official DeepSeek Integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware (permits local frontend dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(brand.router)
app.include_router(knowledge.router)
app.include_router(products.router)
app.include_router(posts.router)
app.include_router(content.router)
app.include_router(research.router)
app.include_router(performance.router)
app.include_router(exports.router)
app.include_router(system.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "deepseek_configured": settings.is_api_key_configured,
        "deepseek_model": settings.deepseek_model
    }

# Mount uploads directory for screenshots and audits
uploads_dir = Path(settings.uploads_dir)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Mount static frontend build if it exists
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
