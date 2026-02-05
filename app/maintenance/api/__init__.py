"""
Maintenance API routers.
"""

from app.maintenance.api import assets, inventory, jobs, pm, procurement, tools, vendors

__all__ = [
    "assets",
    "jobs",
    "inventory",
    "tools",
    "vendors",
    "procurement",
    "pm",
]
