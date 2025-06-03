from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID

from src.applications.schemas import ApplicationCreate, ApplicationRead
from src.applications.dependencies import get_application_service, valid_application_id
from src.applications.service import ApplicationService

router = APIRouter()


@router.post("/", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreate,
    service: ApplicationService = Depends(get_application_service),
):
    return await service.create_application(data)


@router.get("/{application_id}", response_model=ApplicationRead)
async def read_application(
    application: dict = Depends(valid_application_id),
):
    return application


@router.get("/", response_model=List[ApplicationRead])
async def list_applications(
    candidate_id: UUID,
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    service: ApplicationService = Depends(get_application_service),
):
    return await service.list_applications(
        candidate_id=candidate_id, limit=limit, offset=offset
    )


@router.patch("/{application_id}/status", response_model=ApplicationRead)
async def update_status(
    application_id: UUID,
    new_status: str = Query(..., regex="^(applied|tested|hired)$"),
    service: ApplicationService = Depends(get_application_service),
):
    updated = await service.update_application_status(application_id, new_status)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return updated
