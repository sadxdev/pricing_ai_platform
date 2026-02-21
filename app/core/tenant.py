from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_user


async def get_tenant_id(
    user: dict = Depends(get_current_user)
) -> int:
    """
    Extract tenant_id from Keycloak JWT token claims.
    The token must contain a tenant_id claim.
    """
    tenant_id = user.get("tenant_id")

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="tenant_id claim missing from token"
        )

    return int(tenant_id)