import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from typing import List, Optional
from uuid import UUID

from src.applications.schemas import (
    ApplicationCreate,
    ApplicationRead,
    TestResultPayload,
    AssignTestPayload,
)
from src.applications.dependencies import get_application_service, valid_application_id
from src.auth.dependencies import authenticated_user, authenticated_admin
from src.auth.models import User

from src.applications.service import ApplicationService
from src.candidates.dependencies import get_candidate_service
from src.candidates.service import CandidateService
from src.config import settings
from src.vacancies.dependencies import get_vacancy_service
from src.vacancies.service import VacancyService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreate,
    current_user: User = Depends(authenticated_user),
    service: ApplicationService = Depends(get_application_service),
    candidate_service: CandidateService = Depends(get_candidate_service),
    vacancy_service: VacancyService = Depends(get_vacancy_service),
):

    candidate = await candidate_service.get_candidate(data.candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )

    vacancy = await vacancy_service.get_vacancy(data.vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vacancy not found"
        )

    try:
        return await service.create_application(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application: {str(e)}",
        )


@router.get("/{application_id}", response_model=ApplicationRead)
async def read_application(
    application: dict = Depends(valid_application_id),
    current_user: User = Depends(authenticated_admin),
):
    try:
        return application
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read application: {str(e)}",
        )


@router.get("/", response_model=List[ApplicationRead])
async def list_applications(
    current_user: User = Depends(authenticated_user),
    candidate_id: Optional[UUID] = None,
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    service: ApplicationService = Depends(get_application_service),
):
    try:
        if current_user.role != "admin":
            candidate_id = current_user.id

        return await service.list_applications(
            candidate_id=candidate_id, limit=limit, offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list applications: {str(e)}",
        )


@router.post("/{application_id}/assign-test", response_model=ApplicationRead)
async def assign_test(
    application_id: UUID,
    payload: AssignTestPayload,
    background_tasks: BackgroundTasks,
    service: ApplicationService = Depends(get_application_service),
    candidate_service: CandidateService = Depends(get_candidate_service),
):
    try:
        app_obj = await service.get_application(application_id)
        if not app_obj:
            raise HTTPException(status_code=404, detail="Application not found")

        candidate = await candidate_service.get_candidate(app_obj.candidate_id)
        if not candidate or not candidate.is_active:
            raise HTTPException(
                status_code=404, detail="Candidate not found or inactive"
            )

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
                    follow_redirects=True,
                )
                resp.raise_for_status()
                session_data = resp.json()

                updated_app = await service.update_application_status(
                    application_id=application_id,
                    new_status="applied",
                    test_session_id=UUID(session_data["id"]),
                )
                if not updated_app:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to update application with test session",
                    )

                return updated_app

            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=502, detail=f"Failed to assign test: {str(e)}"
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign test: {str(e)}",
        )


@router.post("/{application_id}/test-result", response_model=ApplicationRead)
async def receive_test_result(
    application_id: UUID,
    payload: TestResultPayload,
    service: ApplicationService = Depends(get_application_service),
):
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update test result: {str(e)}",
        )
