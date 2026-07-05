from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from app.utils.logger import setup_logger
from app.api.routes import router as api_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api.security import limiter

from app.api.auth_routes import router as auth_router

logger = setup_logger(__name__)

app = FastAPI(
    title="PO Matching & Invoice Validation API",
    description="API for validating invoices against purchase orders."
)

# Note: In a real production deployment, CORS should be tightened further
# to only allow specific domains (e.g. your production frontend URL), rather 
# than relying on local dev addresses.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

# Mount static files for the frontend UI
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return RedirectResponse(url="/static/index.html")
