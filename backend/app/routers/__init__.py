from app.routers.reports import router as reports_router
from app.routers.incidents import router as incidents_router
from app.routers.ai import router as ai_router
from app.routers.analytics import router as analytics_router
from app.routers.audit import router as audit_router
from app.routers.demo import router as demo_router

__all__ = [
    "reports_router",
    "incidents_router",
    "ai_router",
    "analytics_router",
    "audit_router",
    "demo_router"
]
