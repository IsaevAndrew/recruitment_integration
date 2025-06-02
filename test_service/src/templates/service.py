from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session
from src.templates.models import TestTemplate
from src.templates.schemas import TestTemplateCreate, TestTemplateUpdate, TestTemplateRead

class TemplateService:
    @staticmethod
    async def create(data: TestTemplateCreate) -> TestTemplateRead:
        async with async_session() as db:
            template = TestTemplate(**data.model_dump())
            db.add(template)
            await db.commit()
            await db.refresh(template)
            return template

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 100) -> List[TestTemplateRead]:
        async with async_session() as db:
            result = await db.execute(
                select(TestTemplate).offset(skip).limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def get_by_id(template_id: UUID) -> Optional[TestTemplateRead]:
        async with async_session() as db:
            return await db.get(TestTemplate, template_id)

    @staticmethod
    async def update(template_id: UUID, data: TestTemplateUpdate) -> Optional[TestTemplateRead]:
        async with async_session() as db:
            template = await db.get(TestTemplate, template_id)
            if not template:
                return None
            
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(template, field, value)
            
            await db.commit()
            await db.refresh(template)
            return template

    @staticmethod
    async def delete(template_id: UUID) -> bool:
        async with async_session() as db:
            template = await db.get(TestTemplate, template_id)
            if not template:
                return False
            
            await db.delete(template)
            await db.commit()
            return True
