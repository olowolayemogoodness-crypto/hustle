from fastapi import APIRouter
from app.services.matching_service import match_workers

router = APIRouter()


@router.post("/match")
def match(data: dict):

    job = data["job"]
    workers = data["workers"]

    results = match_workers(job, workers)

    return {
        "matches": results[:10]
    }