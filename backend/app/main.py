import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app.seed.seed_data import seed_database
from app.models.incident import Incident
from app.routers import (
    reports_router,
    incidents_router,
    ai_router,
    analytics_router,
    audit_router,
    demo_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ensure tables created
    Base.metadata.create_all(bind=engine)
    
    # 2. Check if DB is empty and auto-seed
    db = SessionLocal()
    try:
        count = db.query(Incident).count()
        if count == 0:
            print("[Startup] Initializing and seeding default emergency database...")
            seed_database(db)
        else:
            print(f"[Startup] Database loaded with {count} existing incidents.")
    finally:
        db.close()
    
    yield
    print("[Shutdown] Emergency Response Assistant backend stopped.")

app = FastAPI(
    title="AI Emergency Response Assistant API",
    description="Intelligent 5-part pipeline turning many messy incoming reports into evolving emergency incidents.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(reports_router)
app.include_router(incidents_router)
app.include_router(ai_router)
app.include_router(analytics_router)
app.include_router(audit_router)
app.include_router(demo_router)

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "AI Emergency Response Assistant",
        "version": "1.0.0",
        "pipeline_stages": ["INGEST", "UNDERSTAND", "EXTRACT", "TRACK", "SHOW"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
