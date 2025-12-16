from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import init_db
from backend.app.routers import (
    auth_router,
    users_router,
    media_router,
    video_router,
    admin_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Y2K Video Editor API",
    description="Backend API for Y2K Video Editor application",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(media_router)
app.include_router(video_router)
app.include_router(admin_router)


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Y2K Video Editor API", "version": "1.0.0"}


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
