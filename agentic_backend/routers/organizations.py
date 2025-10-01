import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from models.auth import Organization
from database import get_async_db
from auth.decorators import require_system_admin

router = APIRouter(prefix="/api/orgs", tags=["Organizations"])

class OrgCreate(BaseModel):
    name: str
    slug: str
    description: str = ""
    is_active: bool = True

class OrgOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str
    is_active: bool

@router.get("/", response_model=List[OrgOut], dependencies=[Depends(require_system_admin)])
async def list_orgs(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Organization))
    orgs = result.scalars().all()
    return orgs

@router.post("/", response_model=OrgOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_system_admin)])
async def create_org(org: OrgCreate, db: AsyncSession = Depends(get_async_db)):
    new_org = Organization(**org.dict())
    db.add(new_org)
    await db.commit()
    await db.refresh(new_org)
    return new_org

@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_system_admin)])
async def delete_org(org_id: uuid.UUID, db: AsyncSession = Depends(get_async_db)):
    org = await db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    await db.delete(org)
    await db.commit()
    return
