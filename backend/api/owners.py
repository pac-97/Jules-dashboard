from fastapi import APIRouter
from services.owner_service import owner_service
from typing import List, Dict, Any

router = APIRouter()

@router.get("")
def get_owners():
    return owner_service.get_owners()

@router.post("")
def update_owners(owners: List[Dict[str, Any]]):
    owner_service.update_owners(owners)
    return {"status": "success"}
