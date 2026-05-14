from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.health   import router as health_router
from app.api.v1.endpoints.match    import router as match_router
from app.api.v1.endpoints.feedback import router as feedback_router
from app.api.v1.endpoints.wallet   import router as wallet_router
from app.api.v1.endpoints.auth     import router as auth_router
from app.api.v1.endpoints.webhook  import router as webhook_router

from app.core.config     import settings
from app.core.logging    import configure_logging, get_logger
from app.core.middleware import request_timing_middleware
from app.db.init_db      import init_models

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Hustle backend")
    await init_models()
    yield
    logger.info("Shutting down Hustle backend")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    return await request_timing_middleware(request, call_next)

# ── match and feedback already have /api/v1 in their router prefix
app.include_router(health_router)
app.include_router(match_router)
app.include_router(feedback_router)

# ── these need the prefix added
app.include_router(auth_router,     prefix="/api/v1")
app.include_router(wallet_router,   prefix="/api/v1")
app.include_router(webhook_router,  prefix="/api/v1")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request payload."},
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )

@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running."}
