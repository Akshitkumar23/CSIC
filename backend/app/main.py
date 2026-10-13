from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
import sys
from typing import Any, Dict

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.v1 import api_router
from backend.app.core.config import settings
from backend.app.repositories.database import check_db_health

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("csic.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Validate runtime environment safety on startup."""
    settings.check_production_safety()
    yield


# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend micro-services for Student Information, Attendance, Marks, Fees, Timetable, and Notices.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routers
app.include_router(api_router, prefix=settings.API_V1_STR)



@app.get("/", summary="Root index")
async def root() -> Dict[str, Any]:
    """API Root index returning operational metadata."""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
    }


@app.get("/health/live", summary="Liveness probe")
async def health_live() -> Dict[str, Any]:
    """Kubernetes / Cloud provider liveness probe.

    Verifies process availability without external dependency checks.
    """
    return {
        "status": "alive",
        "service": "csic-backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/ready", summary="Readiness probe")
async def health_ready() -> JSONResponse:
    """Kubernetes / Cloud provider readiness probe.

    Verifies whether database connectivity or fallback data store is responsive.
    """
    is_healthy = await check_db_health()
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_healthy else "degraded",
            "database": "connected" if is_healthy else "unreachable",
            "service": "csic-backend",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
