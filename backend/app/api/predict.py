from fastapi import APIRouter
from app.ml.model import predict_success

router = APIRouter()

@router.post("/predict")
def predict(data: dict):
    prob = predict_success(data)
    return {
        "success_probability" : prob
    }