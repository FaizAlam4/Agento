from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload
from models.auth import User, Role, Permission, UserRole, RolePermission
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RBACManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        organization_id: Optional[str] = None
    ) -> bool:
        """Check if user has permission for resource.action"""
        try:
            query = text("""
                SELECT COUNT(*) FROM users u
                JOIN user_roles ur ON u.id = ur.user_id  
                JOIN roles r ON ur.role_id = r.id
                JOIN role_permissions rp ON r.id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE u.id = :user_id 
                AND p.resource = :resource 
                AND p.action = :action
                AND u.is_active = true
                AND ur.is_active = true
                AND (ur.expires_at IS NULL OR ur.expires_at > NOW())
                AND (:org_id IS NULL OR u.organization_id = :org_id OR r.is_system_role = true)
            """)
            
            result = await self.db.execute(query, {
                'user_id': user_id,
                'resource': resource,
                'action': action,
                'org_id': organization_id
            })
            
            count = result.scalar()
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False

    async def get_user_permissions(self, user_id: str) -> List[Dict]:
        """Get all permissions for a user"""
        try:
            query = text("""
                SELECT DISTINCT p.resource, p.action, p.name, p.description
                FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                JOIN roles r ON ur.role_id = r.id  
                JOIN role_permissions rp ON r.id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE u.id = :user_id
                AND u.is_active = true
                AND ur.is_active = true
                AND (ur.expires_at IS NULL OR ur.expires_at > NOW())
                ORDER BY p.resource, p.action
            """)
            
            result = await self.db.execute(query, {'user_id': user_id})
            return [
                {
                    "resource": row.resource,
                    "action": row.action,
                    "name": row.name,
                    "description": row.description
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return []

    async def get_user_roles(self, user_id: str) -> List[Dict]:
        """Get all roles for a user"""
        try:
            query = select(Role).join(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.is_active == True
            )
            
            result = await self.db.execute(query)
            roles = result.scalars().all()
            
            return [
                {
                    "id": str(role.id),
                    "name": role.name,
                    "description": role.description,
                    "is_system_role": role.is_system_role
                }
                for role in roles
            ]
            
        except Exception as e:
            logger.error(f"Error getting user roles: {e}")
            return []

    async def assign_role(
        self,
        user_id: str,
        role_id: str,
        assigned_by: str,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """Assign role to user"""
        try:
            # Check if assignment already exists
            existing = await self.db.execute(
                select(UserRole).where(
                    UserRole.user_id == user_id,
                    UserRole.role_id == role_id
                )
            )
            
            if existing.scalar():
                # Update existing assignment
                await self.db.execute(
                    text("""
                        UPDATE user_roles 
                        SET is_active = true, expires_at = :expires_at, assigned_by = :assigned_by
                        WHERE user_id = :user_id AND role_id = :role_id
                    """),
                    {
                        'user_id': user_id,
                        'role_id': role_id,
                        'assigned_by': assigned_by,
                        'expires_at': expires_at
                    }
                )
            else:
                # Create new assignment
                user_role = UserRole(
                    user_id=user_id,
                    role_id=role_id,
                    assigned_by=assigned_by,
                    expires_at=expires_at
                )
                self.db.add(user_role)
            
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error assigning role: {e}")
            await self.db.rollback()
            return False

    async def revoke_role(self, user_id: str, role_id: str) -> bool:
        """Revoke role from user"""
        try:
            await self.db.execute(
                text("""
                    UPDATE user_roles 
                    SET is_active = false 
                    WHERE user_id = :user_id AND role_id = :role_id
                """),
                {'user_id': user_id, 'role_id': role_id}
            )
            
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error revoking role: {e}")
            await self.db.rollback()
            return False

    async def seed_roles(self, session: AsyncSession):
        """Seed only super-admin and org-admin roles"""
        for role_name, desc in [("super-admin", "System super admin"), ("org-admin", "Organization admin")]:
            result = await session.execute(select(Role).where(Role.name == role_name))
            if not result.scalar():
                session.add(Role(name=role_name, description=desc, is_system_role=(role_name=="super-admin")))
        await session.commit()

    async def create_role(
        self,
        name: str,
        description: str,
        organization_id: Optional[str] = None,
        created_by: str = None,
        is_system_role: bool = False
    ) -> Optional[Role]:
        """Create only super-admin or org-admin role"""
        if name not in ["super-admin", "org-admin"]:
            logger.error(f"Role creation denied: {name} is not allowed.")
            return None
        try:
            role = Role(
                name=name,
                description=description,
                organization_id=organization_id,
                created_by=created_by,
                is_system_role=(name=="super-admin")
            )
            self.db.add(role)
            await self.db.commit()
            await self.db.refresh(role)
            return role
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            await self.db.rollback()
            return None

    async def assign_permission_to_role(
        self,
        role_id: str,
        permission_id: str,
        granted_by: str
    ) -> bool:
        """Assign permission to role"""
        try:
            # Check if assignment already exists
            existing = await self.db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id
                )
            )
            
            if not existing.scalar():
                role_permission = RolePermission(
                    role_id=role_id,
                    permission_id=permission_id,
                    granted_by=granted_by
                )
                self.db.add(role_permission)
                await self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error assigning permission to role: {e}")
            await self.db.rollback()
            return False

    async def get_all_permissions(self) -> List[Permission]:
        """Get all available permissions"""
        try:
            result = await self.db.execute(
                select(Permission).order_by(Permission.resource, Permission.action)
            )
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting permissions: {e}")
            return []

    async def get_all_roles(self, organization_id: Optional[str] = None) -> List[Role]:
        """Get all roles for organization"""
        try:
            query = select(Role)
            if organization_id:
                query = query.where(
                    (Role.organization_id == organization_id) | 
                    (Role.is_system_role == True)
                )
            
            result = await self.db.execute(query.order_by(Role.name))
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting roles: {e}")
            return []