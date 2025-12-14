from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from .database import current_tenant_id
from .models import Tenant


async def set_current_tenant(
    db: Session,
    x_tenant_id: int | None = Header(default=None, alias="X-Tenant-ID"),
) -> int:
    """
    Resolve and set current tenant in ContextVar.
    This should be called as a dependency in your routes.
    """
    if x_tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID header required",
        )

    tenant = db.get(Tenant, x_tenant_id)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    current_tenant_id.set(tenant.id)
    return tenant.id