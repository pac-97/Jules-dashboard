from fastapi import APIRouter
from services.owner_service import owner_service
from services.aws_service import aws_service
from typing import List, Dict, Any

router = APIRouter()

@router.get("")
def get_owners():
    return owner_service.get_owners()

@router.post("")
def update_owners(owners: List[Dict[str, Any]]):
    owner_service.update_owners(owners)
    return {"status": "success"}

@router.post("/sync")
def sync_aws_accounts():
    aws_accounts = aws_service.get_all_accounts()
    result = owner_service.sync_accounts(aws_accounts)
    return {"status": "success", "synced": result["synced"], "total_aws_accounts": len(aws_accounts)}
