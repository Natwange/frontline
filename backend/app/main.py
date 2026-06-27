from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api import chat, dashboard, false_positive, simulator

app = FastAPI(
    title="Frontline Security Gateway",
    description="AI agent protection pipeline for CloudDesk",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(false_positive.router, prefix="/api")
app.include_router(simulator.router, prefix="/api")


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "Frontline Security Gateway"}
