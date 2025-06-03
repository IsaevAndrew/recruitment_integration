import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from typing import List
from uuid import UUID

from src.applications.schemas import (
    ApplicationCreate,
    ApplicationRead,
    TestResultPayload,
)
from src.applications.dependencies import get_application_service, valid_application_id
from src.applications.service import ApplicationService
from src.config import settings

router = APIRouter(prefix="/applications", tags=["applications"])


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


@router.post("/{application_id}/assign-test", response_model=ApplicationRead)
async def assign_test(
    application_id: UUID,
    background_tasks: BackgroundTasks,
    service: ApplicationService = Depends(get_application_service),
):
    """
    HR назначает тест для данного отклика:
    — отправляем POST в test_service /sessions,
    — сохраняем возвращённый session_id в job_applications.test_session_id.
    """
    app_obj = await service.get_application(application_id)
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    payload = {
        "application_id": str(application_id),
        "template_id": str("template-uuid-PLACEHOLDER"),
        # Замените на фактический UUID шаблона из test_service
        "candidate_email": app_obj.candidate_id and app_obj.candidate.email,
        # предполагается, что в frontend передаётся email
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{settings.TEST_SERVICE_URL}/sessions", json=payload, timeout=10.0
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Cannot reach test service",
            )

    if resp.status_code != status.HTTP_201_CREATED:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Test service returned {resp.status_code}",
        )

    data = resp.json()
    session_id = data.get("id") or data.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from test service",
        )

    updated = await service.update_application_status(
        application_id, new_status="applied", test_session_id=UUID(session_id)
    )
    return updated


@router.post("/{application_id}/test-result", response_model=ApplicationRead)
async def receive_test_result(
    application_id: UUID,
    payload: TestResultPayload,
    service: ApplicationService = Depends(get_application_service),
):
    app_obj = await service.get_application(application_id)
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    updated = await service.update_application_status(
        application_id,
        new_status="tested",
        test_session_id=payload.session_id,
        test_score=payload.score,
    )
    return updated
