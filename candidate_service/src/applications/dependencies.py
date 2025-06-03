from fastapi import HTTPException, status, Depends
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.applications.service import ApplicationService


async def get_application_service(
    db: AsyncSession = Depends(get_db),
) -> ApplicationService:
    return ApplicationService(db)


async def valid_application_id(
    application_id: UUID,
    service: ApplicationService = Depends(get_application_service),
) -> dict:
    application = await service.get_application(application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return application
