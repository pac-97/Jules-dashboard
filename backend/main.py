import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Serve frontend static files
# When built via Docker, the frontend dist is copied to /app/static
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Allow serving arbitrary files from the root of the static dir (e.g. favicon.ico, manifest.json)
        # Otherwise, return index.html for React Router compatibility
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
