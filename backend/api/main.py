"""
FastAPI application entry point for Survey Platform.

Wraps existing Python survey generation scripts with REST API.
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add directories to Python path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))  # Add backend to path
sys.path.insert(0, str(BACKEND_DIR / "core"))  # Add core to path

# Import routes
from api.routes import brief, survey, project, data, analysis

# Create FastAPI app
app = FastAPI(
    title="Survey Platform API",
    description="AI-powered survey generation platform",
    version="0.1.0"
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(brief.router, prefix="/api", tags=["brief"])
app.include_router(survey.router, prefix="/api", tags=["survey"])
app.include_router(project.router, prefix="/api", tags=["project"])
app.include_router(data.router, prefix="/api", tags=["data"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Survey Platform API",
        "version": "0.1.0"
    }


@app.get("/api/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "skills_loaded": len(list((BACKEND_DIR.parent / "skills").glob("*.md"))),
        "environment": "development" if os.getenv("DEBUG", "true") == "true" else "production"
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"🚀 Starting Survey Platform API on {host}:{port}")
    print(f"📚 Swagger docs: http://{host}:{port}/docs")
    print(f"📖 ReDoc: http://{host}:{port}/redoc")
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=[str(BACKEND_DIR / "api"), str(BACKEND_DIR / "core")],
        log_level="info"
    )
