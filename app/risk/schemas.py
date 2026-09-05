from pydantic import BaseModel


class RiskRequest(BaseModel):

    glucose: float
    hba1c: float
    weight: float
    height: float
    weekly_activity_minutes: int



class RiskResponse(BaseModel):

    risk_score: int
    risk_level: str
    message: str