from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.applications.schemas import ApplicationCreate, ApplicationUpdate, ApplicationRead
from src.applications.service import ApplicationService
from src.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/applications",
    tags=["applications"]
)

@router.post("/", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    return await ApplicationService.create(db, data)

@router.get("/", response_model=List[ApplicationRead])
async def list_applications(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    return await ApplicationService.get_all(db, skip, limit)

@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    application = await ApplicationService.get_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    return application

@router.patch("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: int,
    data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    application = await ApplicationService.update(db, application_id, data)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    return application

@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    success = await ApplicationService.delete(db, application_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
