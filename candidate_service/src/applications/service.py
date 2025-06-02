from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.applications.models import JobApplication
from src.applications.schemas import ApplicationCreate, ApplicationUpdate, \
    ApplicationRead
from src.candidates.models import Candidate
from src.vacancies.models import Vacancy
from src.utils import create_test_session


class ApplicationService:
    @staticmethod
    async def create(db: AsyncSession,
                     data: ApplicationCreate) -> JobApplication:
        candidate = await db.get(Candidate, data.candidate_id)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )

        vacancy = await db.get(Vacancy, data.vacancy_id)
        if not vacancy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vacancy not found"
            )

        application = JobApplication(
            candidate_id=data.candidate_id,
            vacancy_id=data.vacancy_id,
            status="new"
        )
        db.add(application)
        await db.commit()
        await db.refresh(application)

        try:
            test_session_id = await create_test_session(
                template_id=str(vacancy.id),
                external_application_id=application.id
            )
            application.test_session_id = test_session_id
            await db.commit()
            await db.refresh(application)
        except Exception as e:
            await db.delete(application)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to create test session: {str(e)}"
            )

        return application

    @staticmethod
    async def get_all(
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100
    ) -> List[JobApplication]:
        result = await db.execute(
            select(JobApplication)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, application_id: int) -> Optional[
        JobApplication]:
        return await db.get(JobApplication, application_id)

    @staticmethod
    async def update(
            db: AsyncSession,
            application_id: int,
            data: ApplicationUpdate
    ) -> Optional[JobApplication]:
        application = await db.get(JobApplication, application_id)
        if not application:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(application, field, value)

        await db.commit()
        await db.refresh(application)
        return application

    @staticmethod
    async def delete(db: AsyncSession, application_id: int) -> bool:
        application = await db.get(JobApplication, application_id)
        if not application:
            return False

        await db.delete(application)
        await db.commit()
        return True
