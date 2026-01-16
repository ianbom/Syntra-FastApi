from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth
from app.database import engine, Base
from app.services.minio import get_minio_client, ensure_bucket_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Create database tables and ensure MinIO bucket exists
    Base.metadata.create_all(bind=engine)
    
    # Ensure MinIO bucket exists
    try:
        client = get_minio_client()
        ensure_bucket_exists(client)
        print("✓ MinIO bucket ready")
    except Exception as e:
        print(f"⚠ MinIO connection warning: {e}")
    
    yield
    
    # Shutdown: cleanup if needed
    pass


app = FastAPI(
    title="Auth API",
    description="FastAPI backend with JWT authentication and MinIO storage",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "API is running"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }
