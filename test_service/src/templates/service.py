from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status

from src.templates.models import TestTemplate
from src.templates.schemas import TemplateCreate, TemplateRead


class TemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_template(self, data: TemplateCreate) -> TemplateRead:
        try:
            new_item = TestTemplate(**data.model_dump(exclude_unset=True))
            self.db.add(new_item)
            await self.db.commit()
            await self.db.refresh(new_item)
            return TemplateRead.model_validate(new_item)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create template: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def get_template(self, template_id: UUID) -> Optional[TemplateRead]:
        try:
            result = await self.db.execute(
                select(TestTemplate).where(TestTemplate.id == template_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                return None
            return TemplateRead.model_validate(obj)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def list_templates(
        self, limit: int = 10, offset: int = 0
    ) -> List[TemplateRead]:
        try:
            result = await self.db.execute(
                select(TestTemplate).limit(limit).offset(offset)
            )
            items = result.scalars().all()
            return [TemplateRead.model_validate(item) for item in items]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def update_template(
        self, template_id: UUID, data: TemplateCreate
    ) -> Optional[TemplateRead]:
        try:
            result = await self.db.execute(
                select(TestTemplate).where(TestTemplate.id == template_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                return None
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(obj, field, value)
            await self.db.commit()
            await self.db.refresh(obj)
            return TemplateRead.model_validate(obj)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update template: {str(e)}",
            )
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

    async def delete_template(self, template_id: UUID) -> bool:
        try:
            result = await self.db.execute(
                select(TestTemplate).where(TestTemplate.id == template_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                return False
            await self.db.delete(obj)
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )
