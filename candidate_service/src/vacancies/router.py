from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from src.vacancies.schemas import VacancyCreate, VacancyRead, VacancyUpdate
from src.vacancies.service import VacancyService

from src.auth.dependencies import get_current_admin

from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.post(
    "/",
    response_model=VacancyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать вакансию (только администратор)"
)
async def create_vacancy(
        data: VacancyCreate,
        _: dict = Depends(get_current_admin)
):
    return await VacancyService.create(data)


@router.get(
    "/",
    response_model=List[VacancyRead],
    summary="Список всех вакансий (любой аутентифицированный пользователь)"
)
async def list_vacancies(
        skip: int = 0,
        limit: int = 100,
        _: dict = Depends(get_current_user)
):
    return await VacancyService.get_all(skip, limit)


@router.get(
    "/{vacancy_id}",
    response_model=VacancyRead,
    summary="Получить вакансию по ID (любой аутентифицированный пользователь)"
)
async def get_vacancy(
        vacancy_id: int,
        _: dict = Depends(get_current_user)
):
    vacancy = await VacancyService.get_by_id(vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Vacancy not found")
    return vacancy


@router.put(
    "/{vacancy_id}",
    response_model=VacancyRead,
    summary="Обновить вакансию по ID (только администратор)"
)
async def update_vacancy(
        vacancy_id: int,
        data: VacancyUpdate,
        _: dict = Depends(get_current_admin)
):
    updated = await VacancyService.update(vacancy_id, data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Vacancy not found")
    return updated


@router.delete(
    "/{vacancy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить вакансию по ID (только администратор)"
)
async def delete_vacancy(
        vacancy_id: int,
        _: dict = Depends(get_current_admin)
):
    success = await VacancyService.delete(vacancy_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Vacancy not found")
    return None
