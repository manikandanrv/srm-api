"""
Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import close_db, init_db

# Import routers
from app.core.api import auth, locations, notifications, users, voice
from app.farm.api import checklists as farm_checklists
from app.farm.api import crops, equipment, fields, harvests, schedules, workers
from app.farm.api import scheduled_tasks
from app.farm.api import tasks as farm_tasks
from app.maintenance.api import assets, inventory, jobs, procurement, tools, vendors
from app.maintenance.api import pm as preventive_maintenance
from app.reports.api import reports


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    if settings.debug:
        await init_db()
    yield
    # Shutdown
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="""
        ## Sri Ramanasramam Operations Management System

        Unified backend API serving two Flutter mobile applications:

        ### NPP Farm App (Nallavanpalem)
        - Green fodder cultivation management for Goshala
        - Task management: sowing, watering, fertilizing, harvesting
        - Tamil voice-first interface for semi-literate workers

        ### Ashram Maintenance App (CMMS)
        - Guest house electrical and plumbing maintenance
        - Asset registry, job cards, inventory management
        - Voice-enabled work order processing

        ### Key Features
        - Tamil vernacular support via Bhashini STT/TTS
        - PIN-based authentication for low-literacy users
        - Offline-first mobile app support
        - Real-time notifications and alerts
        """,
        version="0.1.0",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    api_prefix = settings.api_v1_prefix

    # Core module routes
    app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
    app.include_router(users.router, prefix=f"{api_prefix}/users", tags=["Users"])
    app.include_router(
        locations.router, prefix=f"{api_prefix}/locations", tags=["Locations"]
    )
    app.include_router(voice.router, prefix=f"{api_prefix}/voice", tags=["Voice (Bhashini)"])
    app.include_router(
        notifications.router, prefix=f"{api_prefix}/notifications", tags=["Notifications"]
    )

    # Farm module routes
    app.include_router(crops.router, prefix=f"{api_prefix}/farm/crops", tags=["Farm - Crops"])
    app.include_router(
        fields.router, prefix=f"{api_prefix}/farm/fields", tags=["Farm - Fields"]
    )
    app.include_router(
        farm_tasks.router, prefix=f"{api_prefix}/farm/tasks", tags=["Farm - Tasks"]
    )
    app.include_router(
        schedules.router, prefix=f"{api_prefix}/farm/schedules", tags=["Farm - Schedules"]
    )
    app.include_router(
        harvests.router, prefix=f"{api_prefix}/farm/harvests", tags=["Farm - Harvests"]
    )
    app.include_router(
        farm_checklists.router,
        prefix=f"{api_prefix}/farm/checklists",
        tags=["Farm - Checklists"],
    )
    app.include_router(
        equipment.router, prefix=f"{api_prefix}/farm/equipment", tags=["Farm - Equipment"]
    )
    app.include_router(
        scheduled_tasks.router,
        prefix=f"{api_prefix}/farm/scheduled-tasks",
        tags=["Farm - Scheduled Tasks"],
    )
    app.include_router(
        workers.router,
        prefix=f"{api_prefix}/farm/workers",
        tags=["Farm - Workers"],
    )

    # Maintenance module routes
    app.include_router(
        assets.router, prefix=f"{api_prefix}/maintenance/assets", tags=["Maintenance - Assets"]
    )
    app.include_router(
        jobs.router, prefix=f"{api_prefix}/maintenance/jobs", tags=["Maintenance - Job Cards"]
    )
    app.include_router(
        inventory.router,
        prefix=f"{api_prefix}/maintenance/inventory",
        tags=["Maintenance - Inventory"],
    )
    app.include_router(
        tools.router, prefix=f"{api_prefix}/maintenance/tools", tags=["Maintenance - Tools"]
    )
    app.include_router(
        vendors.router,
        prefix=f"{api_prefix}/maintenance/vendors",
        tags=["Maintenance - Vendors"],
    )
    app.include_router(
        procurement.router,
        prefix=f"{api_prefix}/maintenance/procurement",
        tags=["Maintenance - Procurement"],
    )
    app.include_router(
        preventive_maintenance.router,
        prefix=f"{api_prefix}/maintenance/pm",
        tags=["Maintenance - Preventive"],
    )

    # Reports module routes
    app.include_router(reports.router, prefix=f"{api_prefix}/reports", tags=["Reports"])

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "app": settings.app_name}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
    )
