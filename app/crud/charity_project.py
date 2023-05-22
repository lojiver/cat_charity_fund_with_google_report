from datetime import timedelta
from typing import Dict, List, Optional, Union

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_project_id_by_name(
            self,
            project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        db_project_id = db_project_id.scalars().first()
        return db_project_id

    async def get_charity_project_by_id(
            self,
            project_id: int,
            session: AsyncSession,
    ) -> Optional[CharityProject]:
        db_project = await session.execute(
            select(CharityProject).where(
                CharityProject.id == project_id
            )
        )
        db_project = db_project.scalars().first()
        return db_project

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession
    ) -> List[Dict[str, Union[str, timedelta]]]:
        projects = await session.execute(select([
            CharityProject.name, CharityProject.description,
            (func.julianday(CharityProject.close_date) - func.julianday(CharityProject.create_date)).label('time_of_collecting')]
        ).where(CharityProject.fully_invested == 1).order_by('time_of_collecting'))
        projects = projects.all()

        result = []
        for row in projects:
            row_dict = dict(row)
            result.append({
                'name': row_dict['name'],
                'description': row_dict['description'],
                'time_of_collecting': f'{round(row_dict["time_of_collecting"], 2)} days',
            })

        return result


charity_project_crud = CRUDCharityProject(CharityProject)
