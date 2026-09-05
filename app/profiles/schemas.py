from datetime import datetime

from pydantic import BaseModel



class ProfileCreate(BaseModel):

    user_id: int
    weight: float
    height: float
    glucose: float
    hba1c: float



class ProfileResponse(BaseModel):

    id: int
    user_id: int
    weight: float
    height: float
    glucose: float
    hba1c: float
    created_at: datetime


    class Config:
        from_attributes = True