from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.health import router as health_router
from app.api.match import router as match_router
from app.api.predict import router as predict_router
from app.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.middleware import request_timing_middleware
from app.ml import model as ml_model

configure_logging()
logger = get_logger(__name__)

app = FastAPI(title=settings.app_name, version=settings.app_version)

# Routes
app.include_router(health_router)
app.include_router(predict_router)
app.include_router(match_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Hustle backend")
    ml_model.load_model()
    if ml_model.check_model_ready():
        logger.info("ML model ready for inference")
    else:
        logger.warning("ML model is not ready: inference will use fallback probabilities")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Hustle backend")


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
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )


@app.get("/")
def root():
    return {"message": f"{settings.app_name} is running."}
