from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status

from src.vacancies.models import Vacancy
from src.vacancies.schemas import VacancyCreate, VacancyRead


class VacancyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_vacancy(self, data: VacancyCreate) -> VacancyRead:
        try:
            existing_vacancy = await self.db.execute(
                select(Vacancy).where(Vacancy.title == data.title)
            )
            if existing_vacancy.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Vacancy with title '{data.title}' already exists",
                )

            new_item = Vacancy(**data.model_dump(exclude_unset=True))
            self.db.add(new_item)
            await self.db.commit()
            await self.db.refresh(new_item)
            return VacancyRead.model_validate(new_item)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create vacancy: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_vacancy(self, vacancy_id: UUID) -> Optional[VacancyRead]:
        try:
            result = await self.db.execute(
                select(Vacancy).where(Vacancy.id == vacancy_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                return None
            return VacancyRead.model_validate(obj)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def list_vacancies(
        self, limit: int = 10, offset: int = 0
    ) -> List[VacancyRead]:
        try:
            result = await self.db.execute(select(Vacancy).limit(limit).offset(offset))
            items = result.scalars().all()
            return [VacancyRead.model_validate(item) for item in items]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def update_vacancy(
        self, vacancy_id: UUID, data: VacancyCreate
    ) -> Optional[VacancyRead]:
        try:
            result = await self.db.execute(
                select(Vacancy).where(Vacancy.id == vacancy_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Vacancy with id {vacancy_id} not found",
                )

            if data.title != obj.title:
                existing_vacancy = await self.db.execute(
                    select(Vacancy).where(Vacancy.title == data.title)
                )
                if existing_vacancy.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Vacancy with title '{data.title}' already exists",
                    )

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(obj, field, value)
            await self.db.commit()
            await self.db.refresh(obj)
            return VacancyRead.model_validate(obj)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update vacancy: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def delete_vacancy(self, vacancy_id: UUID) -> bool:
        try:
            result = await self.db.execute(
                select(Vacancy).where(Vacancy.id == vacancy_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Vacancy with id {vacancy_id} not found",
                )

            await self.db.delete(obj)
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )
