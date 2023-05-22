from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Extra, Field, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid
        orm_mode = True


class DonationCreate(DonationBase):
    pass


class DonationAdminDB(DonationBase):
    id: int
    create_date: datetime
    user_id: int
    invested_amount: int = Field(0)
    fully_invested: bool
    close_date: Optional[datetime]


class DonationDB(DonationBase):
    id: int
    create_date: datetime
