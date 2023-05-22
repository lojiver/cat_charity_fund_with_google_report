from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.models import CharityProject, User
from app.crud.donation import donations_crud
from app.schemas import (
    DonationAdminDB, DonationCreate, DonationDB
)

router = APIRouter()


@router.get(
    '/',
    response_model=List[DonationAdminDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров.
    Получает список всех пожертвований.
    """
    donation = await donations_crud.get_multi(session)
    return donation


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    new_donation = await donations_crud.create(donation, session, user)
    new_donation = await donations_crud.investing_process(new_donation, CharityProject, session)
    return new_donation


@router.get(
    '/my/',
    response_model=List[DonationDB],
    response_model_exclude={'user_id'},
)
async def get_user_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    donations = await donations_crud.get_by_user(
        session=session, user=user)
    return donations