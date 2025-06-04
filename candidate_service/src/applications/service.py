from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status

from src.applications.models import JobApplication
from src.applications.schemas import (
    ApplicationCreate,
    ApplicationRead,
    TestResultPayload,
)


class ApplicationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_application(self, data: ApplicationCreate) -> ApplicationRead:
        try:
            new_item = JobApplication(**data.model_dump(exclude_unset=True))
            self.db.add(new_item)
            await self.db.commit()
            await self.db.refresh(new_item)
            return ApplicationRead.model_validate(new_item)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create application: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_application(self, application_id: UUID) -> Optional[ApplicationRead]:
        try:
            result = await self.db.execute(
                select(JobApplication).where(JobApplication.id == application_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                return None
            return ApplicationRead.model_validate(obj)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def list_applications(
        self, candidate_id: Optional[UUID] = None, limit: int = 10, offset: int = 0
    ) -> List[ApplicationRead]:
        try:
            query = select(JobApplication)
            if candidate_id is not None:
                query = query.where(JobApplication.candidate_id == candidate_id)
            query = query.limit(limit).offset(offset)

            result = await self.db.execute(query)
            items = result.scalars().all()
            return [ApplicationRead.model_validate(item) for item in items]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def update_application_status(
        self,
        application_id: UUID,
        new_status: str,
        test_session_id: Optional[UUID] = None,
        test_score: Optional[int] = None,
    ) -> Optional[ApplicationRead]:
        try:
            # Check if application exists
            result = await self.db.execute(
                select(JobApplication).where(JobApplication.id == application_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Application with id {application_id} not found",
                )

            # Validate status
            valid_statuses = ["applied", "tested", "hired"]
            if new_status not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                )

            obj.status = new_status
            if test_session_id is not None:
                obj.test_session_id = test_session_id
            if test_score is not None:
                obj.test_score = test_score

            await self.db.commit()
            await self.db.refresh(obj)
            return ApplicationRead.model_validate(obj)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update application status: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_application(self, application_id: UUID) -> Optional[ApplicationRead]:
        result = await self.db.execute(
            select(JobApplication).where(JobApplication.id == application_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        return ApplicationRead.model_validate(obj)
