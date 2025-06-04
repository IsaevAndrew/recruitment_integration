from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID

from src.vacancies.schemas import VacancyCreate, VacancyRead
from src.vacancies.dependencies import get_vacancy_service, valid_vacancy_id
from src.vacancies.service import VacancyService
from src.auth.dependencies import authenticated_user, authenticated_admin
from src.auth.models import User

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.post("/", response_model=VacancyRead, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    data: VacancyCreate,
    current_user: User = Depends(authenticated_admin),
    service: VacancyService = Depends(get_vacancy_service),
):
    try:
        return await service.create_vacancy(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create vacancy: {str(e)}",
        )


@router.get("/{vacancy_id}", response_model=VacancyRead)
async def read_vacancy(
    vacancy: dict = Depends(valid_vacancy_id),
):
    try:
        return vacancy
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read vacancy: {str(e)}",
        )


@router.get("/", response_model=List[VacancyRead])
async def list_vacancies(
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    service: VacancyService = Depends(get_vacancy_service),
):
    try:
        return await service.list_vacancies(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list vacancies: {str(e)}",
        )


@router.put("/{vacancy_id}", response_model=VacancyRead)
async def update_vacancy(
    vacancy_id: UUID,
    data: VacancyCreate,
    current_user: User = Depends(authenticated_admin),
    service: VacancyService = Depends(get_vacancy_service),
):
    try:
        updated = await service.update_vacancy(vacancy_id, data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found"
            )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update vacancy: {str(e)}",
        )


@router.delete("/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy(
    vacancy_id: UUID,
    current_user: User = Depends(authenticated_admin),
    service: VacancyService = Depends(get_vacancy_service),
):
    try:
        deleted = await service.delete_vacancy(vacancy_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete vacancy: {str(e)}",
        )
