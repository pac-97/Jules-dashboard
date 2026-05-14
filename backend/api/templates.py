from fastapi import APIRouter
from services.template_service import template_service
from typing import List, Dict, Any

router = APIRouter()

@router.get("/")
def get_templates():
    return template_service.get_templates()

@router.post("/")
def update_templates(templates: List[Dict[str, Any]]):
    template_service.update_templates(templates)
    return {"status": "success"}
