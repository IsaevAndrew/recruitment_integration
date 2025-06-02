from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.vacancies.schemas import VacancyCreate, VacancyUpdate, VacancyRead
from src.vacancies.models import Vacancy
from src.database import async_session


class VacancyService:
    @staticmethod
    async def create(data: VacancyCreate) -> VacancyRead:
        async with async_session() as session:
            db_obj = Vacancy(
                title=data.title,
                description=data.description
            )
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return VacancyRead.from_orm(db_obj)

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 100) -> List[VacancyRead]:
        async with async_session() as session:
            stmt = select(Vacancy).offset(skip).limit(limit)
            result = await session.execute(stmt)
            vacancies = result.scalars().all()
            return [VacancyRead.from_orm(obj) for obj in vacancies]

    @staticmethod
    async def get_by_id(vacancy_id: int) -> Optional[VacancyRead]:
        async with async_session() as session:
            stmt = select(Vacancy).where(Vacancy.id == vacancy_id)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            if not obj:
                return None
            return VacancyRead.from_orm(obj)

    @staticmethod
    async def update(vacancy_id: int, data: VacancyUpdate) -> Optional[
        VacancyRead]:
        async with async_session() as session:
            stmt = select(Vacancy).where(Vacancy.id == vacancy_id)
            result = await session.execute(stmt)
            obj: Vacancy = result.scalar_one_or_none()
            if not obj:
                return None
            update_data = data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(obj, field, value)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return VacancyRead.from_orm(obj)

    @staticmethod
    async def delete(vacancy_id: int) -> bool:
        async with async_session() as session:
            stmt = select(Vacancy).where(Vacancy.id == vacancy_id)
            result = await session.execute(stmt)
            obj: Vacancy = result.scalar_one_or_none()
            if not obj:
                return False
            await session.delete(obj)
            await session.commit()
            return True
