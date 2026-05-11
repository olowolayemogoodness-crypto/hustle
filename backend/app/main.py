from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.predict import router as predict_router
from app.api.match import router as match_router

app = FastAPI(
    title="Hustle Backend",
    version="1.0.0"
)

# Routes
app.include_router(health_router)
app.include_router(predict_router)
app.include_router(match_router)


@app.get("/")
def root():
    return {"message": "Hustle Backend is running"}