from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def get_healthcheck():
    return {"status": "ok"}
