from fastapi import APIRouter

from app.risk.schemas import (
    RiskRequest,
    RiskResponse
)

from app.risk.service import RiskService



router = APIRouter(
    prefix="/api/v1/risk",
    tags=["Risk Engine"]
)



@router.post(
    "",
    response_model=RiskResponse
)
def calculate_risk(
    data: RiskRequest
):

    return RiskService.calculate_risk(
        data
    )