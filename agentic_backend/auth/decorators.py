from functools import wraps
from typing import List, Tuple
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .rbac import RBACManager
from .dependencies import get_current_user
from database import get_async_db
from models.auth import User

def require_permission(resource: str, action: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user and db from kwargs or dependencies
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication dependencies not properly configured"
                )
            
            rbac = RBACManager(db)
            
            has_permission = await rbac.check_permission(
                user_id=str(current_user.id),
                resource=resource,
                action=action,
                organization_id=str(current_user.organization_id) if current_user.organization_id else None
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {resource}.{action}"
                )
                
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_any_permission(permissions: List[Tuple[str, str]]):
    """Decorator to require any of the specified permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication dependencies not properly configured"
                )
            
            rbac = RBACManager(db)
            
            has_any_permission = False
            for resource, action in permissions:
                if await rbac.check_permission(
                    user_id=str(current_user.id),
                    resource=resource,
                    action=action,
                    organization_id=str(current_user.organization_id) if current_user.organization_id else None
                ):
                    has_any_permission = True
                    break
            
            if not has_any_permission:
                required_perms = [f"{r}.{a}" for r, a in permissions]
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required any of: {required_perms}"
                )
                
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_organization_access(func):
    """Decorator to ensure user belongs to organization"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        organization_id = kwargs.get('organization_id')
        db = kwargs.get('db')
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if organization_id and str(current_user.organization_id) != organization_id:
            # Check if user has system admin role
            rbac = RBACManager(db)
            is_system_admin = await rbac.check_permission(
                user_id=str(current_user.id),
                resource="system",
                action="admin"
            )
            
            if not is_system_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Organization mismatch"
                )
                
        return await func(*args, **kwargs)
    return wrapper

def require_system_admin(func):
    """Decorator to require system admin privileges"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        db = kwargs.get('db')
        
        if not current_user or not db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        rbac = RBACManager(db)
        is_system_admin = await rbac.check_permission(
            user_id=str(current_user.id),
            resource="system",
            action="admin"
        )
        
        if not is_system_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="System administrator privileges required"
            )
            
        return await func(*args, **kwargs)
    return wrapper

def require_org_admin(func):
    """Decorator to require org-admin privileges"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        db = kwargs.get('db')
        if not current_user or not db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        # Check if user has org-admin role
        rbac = RBACManager(db)
        roles = await rbac.get_user_roles(str(current_user.id))
        if not any(role['name'] == 'org-admin' for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization administrator privileges required"
            )
        return await func(*args, **kwargs)
    return wrapper