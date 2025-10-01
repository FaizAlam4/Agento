# RBAC (Role-Based Access Control) Documentation

## 🎯 Overview

The Smart Customer Support system implements a comprehensive Role-Based Access Control (RBAC) system to ensure secure access to resources and functionality based on user roles and permissions.

## 🏗️ RBAC Architecture

### Core Components

```
Users ←→ User_Roles ←→ Roles ←→ Role_Permissions ←→ Permissions
  ↓                                                        ↓
Organizations                                         Resources + Actions
```

### Entities Description

1. **Users**: Individual system users with authentication credentials
2. **Roles**: Named collections of permissions (e.g., "Admin", "Team Lead")
3. **Permissions**: Specific actions on resources (e.g., "knowledge_base.create")
4. **Organizations**: Tenant isolation for multi-org deployments
5. **Resources**: System entities (knowledge_base, analytics, users, etc.)
6. **Actions**: Operations (create, read, update, delete, admin)

## 👥 Role Hierarchy

### System Roles

#### 1. **Super Admin**
- **Scope**: Global system administration
- **Permissions**:
  - `system.admin` - Full system configuration
  - `organization.*` - Manage all organizations
  - `user.*` - Manage all users
  - `analytics.admin` - Access all analytics
  - `knowledge_base.*` - Manage all knowledge bases
  - `audit.read` - View audit logs

#### 2. **Organization Admin**
- **Scope**: Single organization administration
- **Permissions**:
  - `organization.read` - View org details
  - `organization.update` - Update org settings
  - `user.create` - Add users to org
  - `user.read` - View org users
  - `user.update` - Modify org users
  - `user.delete` - Remove org users
  - `knowledge_base.*` - Manage org knowledge bases
  - `analytics.read` - View org analytics
  - `scraping.admin` - Configure scraping rules

#### 3. **Team Lead**
- **Scope**: Team management within organization
- **Permissions**:
  - `user.read` - View team members
  - `user.invite` - Invite new team members
  - `knowledge_base.create` - Create team knowledge bases
  - `knowledge_base.read` - Access team knowledge bases
  - `knowledge_base.update` - Modify team knowledge bases
  - `analytics.read` - View team analytics
  - `conversation.read` - View team conversations

#### 4. **Regular User**
- **Scope**: Standard user functionality
- **Permissions**:
  - `knowledge_base.read` - Access assigned knowledge bases
  - `conversation.create` - Start new conversations
  - `conversation.read` - View own conversations
  - `conversation.update` - Update own conversations
  - `scraping.submit` - Submit URLs for scraping
  - `profile.read` - View own profile
  - `profile.update` - Update own profile

#### 5. **Guest User**
- **Scope**: Limited read-only access
- **Permissions**:
  - `knowledge_base.read` - Access public knowledge bases
  - `conversation.create` - Limited conversation access
  - `conversation.read` - View own conversations only

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    is_system_user BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    organization_id UUID REFERENCES organizations(id),
    created_by UUID REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_organization_id ON users(organization_id);
CREATE INDEX idx_users_is_active ON users(is_active);
```

### Organizations Table
```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_organizations_slug ON organizations(slug);
CREATE INDEX idx_organizations_is_active ON organizations(is_active);
```

### Roles Table
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT false,
    is_default BOOLEAN DEFAULT false,
    organization_id UUID REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT unique_role_per_org UNIQUE(name, organization_id)
);

-- Indexes
CREATE INDEX idx_roles_organization_id ON roles(organization_id);
CREATE INDEX idx_roles_is_system_role ON roles(is_system_role);
```

### Permissions Table
```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    is_system_permission BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_resource_action UNIQUE(resource, action)
);

-- Indexes
CREATE INDEX idx_permissions_resource ON permissions(resource);
CREATE INDEX idx_permissions_action ON permissions(action);
CREATE INDEX idx_permissions_resource_action ON permissions(resource, action);
```

### User-Role Mapping
```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    CONSTRAINT unique_user_role UNIQUE(user_id, role_id)
);

-- Indexes
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX idx_user_roles_is_active ON user_roles(is_active);
```

### Role-Permission Mapping
```sql
CREATE TABLE role_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_role_permission UNIQUE(role_id, permission_id)
);

-- Indexes
CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);
```

### Audit Log
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
```

## 🔧 Backend Implementation

### Permission Checker
```python
# auth/rbac.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import Depends, HTTPException, status

class RBACManager:
    def __init__(self, db: Session):
        self.db = db
        
    def check_permission(
        self, 
        user_id: str, 
        resource: str, 
        action: str,
        organization_id: Optional[str] = None
    ) -> bool:
        """Check if user has permission for resource.action"""
        
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
        
        result = self.db.execute(query, {
            'user_id': user_id,
            'resource': resource, 
            'action': action,
            'org_id': organization_id
        })
        
        return result.scalar() > 0
        
    def get_user_permissions(self, user_id: str) -> List[dict]:
        """Get all permissions for a user"""
        
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
        
        result = self.db.execute(query, {'user_id': user_id})
        return [dict(row) for row in result]
        
    def assign_role(
        self, 
        user_id: str, 
        role_id: str, 
        assigned_by: str,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """Assign role to user"""
        
        try:
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                assigned_by=assigned_by,
                expires_at=expires_at
            )
            self.db.add(user_role)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False
```

### Permission Decorators
```python
# auth/decorators.py
from functools import wraps
from fastapi import Depends, HTTPException, status
from .rbac import RBACManager
from .jwt_handler import get_current_user

def require_permission(resource: str, action: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract dependencies
            current_user = kwargs.get('current_user') or get_current_user()
            db = kwargs.get('db')
            
            rbac = RBACManager(db)
            
            if not rbac.check_permission(
                user_id=current_user.id,
                resource=resource,
                action=action,
                organization_id=current_user.organization_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {resource}.{action}"
                )
                
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_any_permission(permissions: List[tuple]):
    """Decorator to require any of the specified permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user') or get_current_user()
            db = kwargs.get('db')
            
            rbac = RBACManager(db)
            
            has_permission = any(
                rbac.check_permission(
                    user_id=current_user.id,
                    resource=resource,
                    action=action,
                    organization_id=current_user.organization_id
                )
                for resource, action in permissions
            )
            
            if not has_permission:
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
        current_user = kwargs.get('current_user') or get_current_user()
        organization_id = kwargs.get('organization_id')
        
        if organization_id and current_user.organization_id != organization_id:
            # Check if user has system admin role
            db = kwargs.get('db')
            rbac = RBACManager(db)
            
            if not rbac.check_permission(
                user_id=current_user.id,
                resource="system",
                action="admin"
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Organization mismatch"
                )
                
        return await func(*args, **kwargs)
    return wrapper
```

### API Endpoint Examples
```python
# api/knowledge_bases.py
from fastapi import APIRouter, Depends, HTTPException
from ..auth.decorators import require_permission, require_organization_access
from ..auth.jwt_handler import get_current_user

router = APIRouter(prefix="/api/knowledge-bases", tags=["knowledge-bases"])

@router.post("/")
@require_permission("knowledge_base", "create")
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new knowledge base"""
    # Implementation
    pass

@router.get("/{kb_id}")
@require_permission("knowledge_base", "read")
async def get_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get knowledge base details"""
    # Check if user has access to this specific KB
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.organization_id == current_user.organization_id
    ).first()
    
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    return kb

@router.delete("/{kb_id}")
@require_permission("knowledge_base", "delete")
async def delete_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete knowledge base"""
    # Implementation with ownership check
    pass

@router.get("/")
@require_permission("knowledge_base", "read")
async def list_knowledge_bases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List accessible knowledge bases"""
    # Return only KBs user has access to
    query = db.query(KnowledgeBase)
    
    # If not system admin, filter by organization
    if not rbac.check_permission(current_user.id, "system", "admin"):
        query = query.filter(
            KnowledgeBase.organization_id == current_user.organization_id
        )
    
    return query.all()
```

## 🎨 Frontend Implementation

### Permission Hook
```typescript
// hooks/usePermissions.ts
import { useAuth } from './useAuth';
import { Permission } from '../types/auth';

interface UsePermissionsReturn {
  hasPermission: (resource: string, action: string) => boolean;
  hasAnyPermission: (permissions: Array<{resource: string, action: string}>) => boolean;
  permissions: Permission[];
  isLoading: boolean;
}

export const usePermissions = (): UsePermissionsReturn => {
    const { user, isLoading } = useAuth();
    
    const hasPermission = (resource: string, action: string): boolean => {
        if (!user?.permissions) return false;
        
        return user.permissions.some(p => 
            p.resource === resource && p.action === action
        );
    };
    
    const hasAnyPermission = (
        permissions: Array<{resource: string, action: string}>
    ): boolean => {
        return permissions.some(({ resource, action }) => 
            hasPermission(resource, action)
        );
    };
    
    return {
        hasPermission,
        hasAnyPermission,
        permissions: user?.permissions || [],
        isLoading
    };
};
```

### Protected Components
```tsx
// components/ProtectedComponent.tsx
import React from 'react';
import { usePermissions } from '../hooks/usePermissions';

interface ProtectedComponentProps {
    resource: string;
    action: string;
    children: React.ReactNode;
    fallback?: React.ReactNode;
    showFallback?: boolean;
}

export const ProtectedComponent: React.FC<ProtectedComponentProps> = ({
    resource,
    action,
    children,
    fallback = null,
    showFallback = true
}) => {
    const { hasPermission, isLoading } = usePermissions();
    
    if (isLoading) {
        return <div>Loading...</div>;
    }
    
    if (!hasPermission(resource, action)) {
        return showFallback ? fallback : null;
    }
    
    return <>{children}</>;
};

// Usage Examples
export const KnowledgeBaseActions = () => {
    return (
        <div className="space-y-2">
            <ProtectedComponent resource="knowledge_base" action="create">
                <CreateKnowledgeBaseButton />
            </ProtectedComponent>
            
            <ProtectedComponent resource="knowledge_base" action="delete">
                <DeleteKnowledgeBaseButton />
            </ProtectedComponent>
            
            <ProtectedComponent 
                resource="analytics" 
                action="read"
                fallback={<div>Analytics access restricted</div>}
            >
                <AnalyticsDashboard />
            </ProtectedComponent>
        </div>
    );
};
```

### Route Protection
```tsx
// components/ProtectedRoute.tsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { usePermissions } from '../hooks/usePermissions';

interface ProtectedRouteProps {
    resource: string;
    action: string;
    children: React.ReactNode;
    redirectTo?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    resource,
    action,
    children,
    redirectTo = '/unauthorized'
}) => {
    const { hasPermission, isLoading } = usePermissions();
    
    if (isLoading) {
        return <div>Loading...</div>;
    }
    
    if (!hasPermission(resource, action)) {
        return <Navigate to={redirectTo} replace />;
    }
    
    return <>{children}</>;
};

// Router setup
const AppRouter = () => {
    return (
        <Routes>
            <Route path="/dashboard" element={
                <ProtectedRoute resource="dashboard" action="read">
                    <Dashboard />
                </ProtectedRoute>
            } />
            
            <Route path="/admin" element={
                <ProtectedRoute resource="system" action="admin">
                    <AdminPanel />
                </ProtectedRoute>
            } />
            
            <Route path="/analytics" element={
                <ProtectedRoute resource="analytics" action="read">
                    <Analytics />
                </ProtectedRoute>
            } />
        </Routes>
    );
};
```

## 🔍 Permission Management

### Default Permissions Seeding
```python
# scripts/seed_permissions.py
from sqlalchemy.orm import Session
from ..models import Permission, Role, RolePermission

DEFAULT_PERMISSIONS = [
    # System permissions
    {"name": "system.admin", "resource": "system", "action": "admin", "description": "Full system administration"},
    
    # User permissions
    {"name": "user.create", "resource": "user", "action": "create", "description": "Create new users"},
    {"name": "user.read", "resource": "user", "action": "read", "description": "View user information"},
    {"name": "user.update", "resource": "user", "action": "update", "description": "Update user information"},
    {"name": "user.delete", "resource": "user", "action": "delete", "description": "Delete users"},
    
    # Knowledge base permissions
    {"name": "knowledge_base.create", "resource": "knowledge_base", "action": "create", "description": "Create knowledge bases"},
    {"name": "knowledge_base.read", "resource": "knowledge_base", "action": "read", "description": "View knowledge bases"},
    {"name": "knowledge_base.update", "resource": "knowledge_base", "action": "update", "description": "Update knowledge bases"},
    {"name": "knowledge_base.delete", "resource": "knowledge_base", "action": "delete", "description": "Delete knowledge bases"},
    
    # Analytics permissions
    {"name": "analytics.read", "resource": "analytics", "action": "read", "description": "View analytics"},
    {"name": "analytics.admin", "resource": "analytics", "action": "admin", "description": "Full analytics access"},
    
    # Conversation permissions
    {"name": "conversation.create", "resource": "conversation", "action": "create", "description": "Start conversations"},
    {"name": "conversation.read", "resource": "conversation", "action": "read", "description": "View conversations"},
    {"name": "conversation.update", "resource": "conversation", "action": "update", "description": "Update conversations"},
    {"name": "conversation.delete", "resource": "conversation", "action": "delete", "description": "Delete conversations"},
    
    # Scraping permissions
    {"name": "scraping.submit", "resource": "scraping", "action": "submit", "description": "Submit URLs for scraping"},
    {"name": "scraping.admin", "resource": "scraping", "action": "admin", "description": "Configure scraping settings"},
]

def seed_permissions(db: Session):
    """Seed default permissions"""
    for perm_data in DEFAULT_PERMISSIONS:
        existing = db.query(Permission).filter(
            Permission.name == perm_data["name"]
        ).first()
        
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
    
    db.commit()
```

## 🛡️ Security Best Practices

### 1. Principle of Least Privilege
- Users get minimum permissions needed for their role
- Regular review and cleanup of unused permissions
- Time-bound role assignments where appropriate

### 2. Permission Granularity
- Fine-grained permissions for better control
- Resource-level and action-level separation
- Organization-scoped permissions

### 3. Audit and Monitoring
- Log all permission changes
- Track permission usage
- Regular access reviews

### 4. Error Handling
- Clear error messages for permission denials
- Avoid information leakage in error responses
- Graceful degradation for missing permissions

## 📊 RBAC Analytics

### Permission Usage Tracking
```sql
-- Track permission usage
CREATE TABLE permission_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    permission_id UUID REFERENCES permissions(id),
    resource_id UUID,
    success BOOLEAN,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Usage analytics queries
-- Most used permissions
SELECT p.name, COUNT(*) as usage_count
FROM permission_usage pu
JOIN permissions p ON pu.permission_id = p.id
WHERE pu.created_at >= NOW() - INTERVAL '30 days'
GROUP BY p.id, p.name
ORDER BY usage_count DESC;

-- Permission denial patterns
SELECT p.name, COUNT(*) as denial_count
FROM permission_usage pu
JOIN permissions p ON pu.permission_id = p.id
WHERE pu.success = false
AND pu.created_at >= NOW() - INTERVAL '7 days'
GROUP BY p.id, p.name
ORDER BY denial_count DESC;
```

This RBAC system provides enterprise-grade security while maintaining flexibility for various organizational structures and access patterns.