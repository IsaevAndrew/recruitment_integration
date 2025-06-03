from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

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
        new_item = JobApplication(**data.model_dump(exclude_unset=True))
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return ApplicationRead.model_validate(new_item)

    async def get_application(self, application_id: UUID) -> Optional[ApplicationRead]:
        result = await self.db.execute(
            select(JobApplication).where(JobApplication.id == application_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        return ApplicationRead.model_validate(obj)

    async def list_applications(
        self, candidate_id: UUID, limit: int = 10, offset: int = 0
    ) -> List[ApplicationRead]:
        result = await self.db.execute(
            select(JobApplication)
            .where(JobApplication.candidate_id == candidate_id)
            .limit(limit)
            .offset(offset)
        )
        items = result.scalars().all()
        return [ApplicationRead.model_validate(item) for item in items]

    async def update_application_status(
        self,
        application_id: UUID,
        new_status: str,
        test_session_id: Optional[UUID] = None,
        test_score: Optional[int] = None,
    ) -> Optional[ApplicationRead]:
        result = await self.db.execute(
            select(JobApplication).where(JobApplication.id == application_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None

        obj.status = new_status
        if test_session_id is not None:
            obj.test_session_id = test_session_id
        if test_score is not None:
            obj.test_score = test_score

        await self.db.commit()
        await self.db.refresh(obj)
        return ApplicationRead.model_validate(obj)
