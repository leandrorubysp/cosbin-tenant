from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import async_session_maker, current_tenant_id
from app.core.casbin import get_casbin_enforcer
from app.models.user import User, Tenant


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


async def get_current_tenant_id(
    db: AsyncSession = Depends(get_db),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> str:
    if x_tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID header required",
        )

    result = await db.execute(select(Tenant).where(Tenant.id == int(x_tenant_id)))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    current_tenant_id.set(x_tenant_id)
    return x_tenant_id


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
) -> User:
    result = await db.execute(
        select(User).where(User.username == "alice", User.tenant_id == int(tenant_id))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in this tenant",
        )
    return user


def casbin_enforce(
    obj: str,
    act: str,
):
    def dependency(
        current_user: User = Depends(get_current_user),
        tenant_id: str = Depends(get_current_tenant_id),
    ):
        e = get_casbin_enforcer()
        if not e.enforce(current_user.username, tenant_id, obj, act):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return True

    return dependency