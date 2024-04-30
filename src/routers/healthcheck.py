from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def get_healthcheck():
    """    Returns a dictionary with the status of the healthcheck.

    Returns:
        dict: A dictionary with the status of the healthcheck.
    """
    return {"status": "ok"}
