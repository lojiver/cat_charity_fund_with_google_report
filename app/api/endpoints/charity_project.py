from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud.charity_project import charity_project_crud
from app.api.validators import (
    check_name_duplicate, check_charity_project_exists,
    check_charity_project_already_invested,
    check_charity_project_invested_sum, check_charity_project_closed
)
from app.models import Donation
from app.schemas import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate)
from app.core.user import current_superuser

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.
    Создает благотворительный проект.
    """
    await check_name_duplicate(charity_project.name, session)
    new_project = await charity_project_crud.create(charity_project, session)
    await charity_project_crud.investing_process(new_project, Donation, session)
    return new_project


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    all_projects = await charity_project_crud.get_multi(session)
    return all_projects


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    # проверка на filly_ivested
    await check_charity_project_closed(charity_project)
    if obj_in.name:
        await check_name_duplicate(obj_in.name, session)
    if obj_in.full_amount:
        # проверка того, что новая сумма больше уже внесённой
        await check_charity_project_invested_sum(charity_project, obj_in.full_amount)
        if obj_in.full_amount == charity_project.invested_amount:
            charity_project_crud.close_donation_for_obj(charity_project)

    charity_project = await charity_project_crud.update(
        charity_project, obj_in, session
    )

    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.
    Удаляет проект. Нельзя удалить проект,
    в который уже были инвестированы средства, его можно только закрыть.
    """
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    await check_charity_project_already_invested(charity_project)
    await check_charity_project_closed(charity_project)
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project
