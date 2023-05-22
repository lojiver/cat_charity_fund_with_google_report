from datetime import datetime
from typing import Optional, List, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, CharityProject, Donation


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession
    ):
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
        user: Optional[User] = None
    ):
        obj_in_data = obj_in.dict()
        if user:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def get_not_full_invested_objects(
        self,
        model: Union[CharityProject, Donation],
        session: AsyncSession
    ) -> List[Union[CharityProject, Donation]]:
        objects = await session.execute(select(model).where(
            model.fully_invested == 0).order_by(model.create_date))
        return objects.scalars().all()

    async def close_donation_for_obj(self, obj_in: Union[CharityProject, Donation]):
        obj_in.invested_amount = obj_in.full_amount
        obj_in.fully_invested = True
        obj_in.close_date = datetime.utcnow()
        return obj_in

    async def invest_money(
        self,
        obj_in: Union[CharityProject, Donation],
        obj_model: Union[CharityProject, Donation],
    ) -> Union[CharityProject, Donation]:
        free_amount_in = obj_in.full_amount - obj_in.invested_amount
        free_amount_in_model = obj_model.full_amount - obj_model.invested_amount

        if free_amount_in > free_amount_in_model:
            obj_in.invested_amount += free_amount_in_model
            obj_model = await self.close_donation_for_obj(obj_model)

        elif free_amount_in == free_amount_in_model:
            obj_in = await self.close_donation_for_obj(obj_in)
            obj_model = await self.close_donation_for_obj(obj_model)

        else:
            obj_model.invested_amount += free_amount_in
            obj_in = await self.close_donation_for_obj(obj_in)

        return obj_in, obj_model

    async def investing_process(
        self,
        obj_in: Union[CharityProject, Donation],
        model_add: Union[CharityProject, Donation],
        session: AsyncSession,
    ) -> Union[CharityProject, Donation]:
        objects_model = await self.get_not_full_invested_objects(model_add, session)

        for model in objects_model:
            obj_in, model = await self.invest_money(obj_in, model)
            session.add(obj_in)
            session.add(model)

        await session.commit()
        await session.refresh(obj_in)
        return obj_in