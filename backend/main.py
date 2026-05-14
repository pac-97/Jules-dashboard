from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api import dashboard, findings, operations, owners, templates, emails
from services.scheduler import init_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_scheduler()
    yield
    shutdown_scheduler()

app = FastAPI(title="AWS Security Dashboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(findings.router, prefix="/api/findings", tags=["Findings"])
app.include_router(operations.router, prefix="/api/operations", tags=["Operations"])
app.include_router(owners.router, prefix="/api/owners", tags=["Owners"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(emails.router, prefix="/api/emails", tags=["Emails"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
