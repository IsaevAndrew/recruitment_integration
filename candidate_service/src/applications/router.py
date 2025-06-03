import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Query, \
    BackgroundTasks
from typing import List
from uuid import UUID

from src.applications.schemas import (
    ApplicationCreate,
    ApplicationRead,
    TestResultPayload, AssignTestPayload,
)
from src.applications.dependencies import get_application_service, \
    valid_application_id

from src.applications.service import ApplicationService
from src.candidates.dependencies import get_candidate_service
from src.candidates.service import CandidateService
from src.config import settings

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=ApplicationRead,
             status_code=status.HTTP_201_CREATED)
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
        payload: AssignTestPayload,
        background_tasks: BackgroundTasks,
        service: ApplicationService = Depends(get_application_service),
        candidate_service: CandidateService = Depends(get_candidate_service),

):
    app_obj = await service.get_application(application_id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    candidate = await candidate_service.get_candidate(app_obj.candidate_id)
    if not candidate or not candidate.is_active:
        raise HTTPException(status_code=404,
                            detail="Candidate not found or inactive")

    session_payload = {
        "application_id": str(app_obj.id),
        "template_id": str(payload.template_id),
        "candidate_email": candidate.email,
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{settings.TEST_SERVICE_URL}/sessions/",
                json=session_payload,
                timeout=10.0,
                follow_redirects=True
            )
            resp.raise_for_status()
            session_data = resp.json()

            updated_app = await service.update_application_status(
                application_id=application_id,
                new_status="applied",
                test_session_id=UUID(session_data["id"])
            )
            if not updated_app:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update application with test session"
                )

            return updated_app

        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to assign test: {str(e)}"
            )


@router.post("/{application_id}/test-result", response_model=ApplicationRead)
async def receive_test_result(
        application_id: UUID,
        payload: TestResultPayload,
        service: ApplicationService = Depends(get_application_service),
):
    app_obj = await service.get_application(application_id)
    if not app_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    updated = await service.update_application_status(
        application_id,
        new_status="tested",
        test_session_id=payload.session_id,
        test_score=payload.score,
    )
    return updated
