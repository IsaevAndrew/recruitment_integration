from fastapi import HTTPException, status, Depends
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.templates.service import TemplateService


async def get_template_service(
        db: AsyncSession = Depends(get_db)) -> TemplateService:
    return TemplateService(db)


async def valid_template_id(
        template_id: UUID,
        service: TemplateService = Depends(get_template_service),
) -> dict:
    template = await service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Template not found")
    return template
