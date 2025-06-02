from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID

from src.templates.schemas import TemplateCreate, TemplateRead
from src.templates.dependencies import get_template_service, valid_template_id
from src.templates.service import TemplateService

router = APIRouter()


@router.post("/", response_model=TemplateRead,
             status_code=status.HTTP_201_CREATED)
async def create_template(
        data: TemplateCreate,
        service: TemplateService = Depends(get_template_service),
):
    return await service.create_template(data)


@router.get("/{template_id}", response_model=TemplateRead)
async def read_template(
        template: dict = Depends(valid_template_id),
):
    return template


@router.get("/", response_model=List[TemplateRead])
async def list_templates(
        limit: int = Query(default=10, ge=1),
        offset: int = Query(default=0, ge=0),
        service: TemplateService = Depends(get_template_service),
):
    return await service.list_templates(limit=limit, offset=offset)


@router.put("/{template_id}", response_model=TemplateRead)
async def update_template(
        template_id: UUID,
        data: TemplateCreate,
        service: TemplateService = Depends(get_template_service),
):
    updated = await service.update_template(template_id, data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Template not found")
    return updated


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
        template_id: UUID,
        service: TemplateService = Depends(get_template_service),
):
    deleted = await service.delete_template(template_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Template not found")
    return None
