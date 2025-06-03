from fastapi import HTTPException, status, Depends
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.vacancies.service import VacancyService


async def get_vacancy_service(db: AsyncSession = Depends(get_db)) -> VacancyService:
    return VacancyService(db)


async def valid_vacancy_id(
    vacancy_id: UUID,
    service: VacancyService = Depends(get_vacancy_service),
) -> dict:
    vacancy = await service.get_vacancy(vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found"
        )
    return vacancy
