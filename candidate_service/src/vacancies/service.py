from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from src.vacancies.models import Vacancy
from src.vacancies.schemas import VacancyCreate, VacancyRead


class VacancyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_vacancy(self, data: VacancyCreate) -> VacancyRead:
        new_item = Vacancy(**data.model_dump(exclude_unset=True))
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return VacancyRead.model_validate(new_item)

    async def get_vacancy(self, vacancy_id: UUID) -> Optional[VacancyRead]:
        result = await self.db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        return VacancyRead.model_validate(obj)

    async def list_vacancies(
        self, limit: int = 10, offset: int = 0
    ) -> List[VacancyRead]:
        result = await self.db.execute(select(Vacancy).limit(limit).offset(offset))
        items = result.scalars().all()
        return [VacancyRead.model_validate(item) for item in items]

    async def update_vacancy(
        self, vacancy_id: UUID, data: VacancyCreate
    ) -> Optional[VacancyRead]:
        result = await self.db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return VacancyRead.model_validate(obj)

    async def delete_vacancy(self, vacancy_id: UUID) -> bool:
        result = await self.db.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
        obj = result.scalar_one_or_none()
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True
