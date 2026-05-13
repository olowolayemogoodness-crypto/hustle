from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.match import router as match_router
from app.api.predict import router as predict_router
from app.api.feedback import router as feedback_router
from app.api.analytics import router as analytics_router
from app.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.middleware import request_timing_middleware
from app.db.init_db import init_models
from app.ml import model as ml_model

configure_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Hustle backend")
    await init_models()
    ml_model.load_model()
    if ml_model.check_model_ready():
        logger.info("ML model ready for inference")
    else:
        logger.warning("ML model is not ready: inference will use fallback probabilities")
    yield
    logger.info("Shutting down Hustle backend")


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

# Routes
app.include_router(health_router)
app.include_router(predict_router)
app.include_router(match_router)
app.include_router(feedback_router)
app.include_router(analytics_router)
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request payload."},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning("HTTP exception on %s %s: %s", request.method, request.url.path, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )


@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running."}
