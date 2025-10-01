from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
import uuid

# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    organization_id: Optional[uuid.UUID] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    is_system_user: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    organization_id: Optional[uuid.UUID]
    
    class Config:
        from_attributes = True

class UserWithPermissions(UserResponse):
    permissions: List['PermissionResponse'] = []
    roles: List['RoleResponse'] = []

# Organization schemas
class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    settings: Optional[dict] = {}

class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    settings: Optional[dict] = None

class OrganizationResponse(OrganizationBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID]
    
    class Config:
        from_attributes = True

# Role schemas
class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class RoleCreate(RoleBase):
    organization_id: Optional[uuid.UUID] = None
    is_system_role: bool = False
    is_default: bool = False

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_default: Optional[bool] = None

class RoleResponse(RoleBase):
    id: uuid.UUID
    is_system_role: bool
    is_default: bool
    created_at: datetime
    organization_id: Optional[uuid.UUID]
    created_by: Optional[uuid.UUID]
    
    class Config:
        from_attributes = True

class RoleWithPermissions(RoleResponse):
    permissions: List['PermissionResponse'] = []

# Permission schemas
class PermissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    resource: str = Field(..., min_length=1, max_length=100)
    action: str = Field(..., min_length=1, max_length=50)

class PermissionCreate(PermissionBase):
    is_system_permission: bool = False

class PermissionResponse(PermissionBase):
    id: uuid.UUID
    is_system_permission: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# User Role schemas
class UserRoleCreate(BaseModel):
    user_id: uuid.UUID
    role_id: uuid.UUID
    expires_at: Optional[datetime] = None

class UserRoleResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID
    assigned_by: Optional[uuid.UUID]
    assigned_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

# Authentication schemas
class LoginRequest(BaseModel):
    username: str  # Can be username or email
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserWithPermissions

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

# Update forward references
UserWithPermissions.model_rebuild()
RoleWithPermissions.model_rebuild()