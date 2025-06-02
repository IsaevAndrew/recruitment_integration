from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.templates.schemas import TestTemplateCreate, TestTemplateRead, TestTemplateUpdate
from src.templates.service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])

@router.post("/", response_model=TestTemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(data: TestTemplateCreate):
    return await TemplateService.create(data)

@router.get("/", response_model=List[TestTemplateRead])
async def list_templates(skip: int = 0, limit: int = 100):
    return await TemplateService.get_all(skip, limit)

@router.get("/{template_id}", response_model=TestTemplateRead)
async def get_template(template_id: str):
    template = await TemplateService.get_by_id(template_id)
    if not template:
        raise HTTPException(404, "Template not found")
    return template

@router.put("/{template_id}", response_model=TestTemplateRead)
async def update_template(template_id: str, data: TestTemplateUpdate):
    updated = await TemplateService.update(template_id, data)
    if not updated:
        raise HTTPException(404, "Template not found")
    return updated

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: str):
    success = await TemplateService.delete(template_id)
    if not success:
        raise HTTPException(404, "Template not found")
    return None