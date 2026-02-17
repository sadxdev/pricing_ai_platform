from fastapi import Header, HTTPException, status


async def get_tenant_id(x_tenant_id: int = Header(...)) -> int:
    """
    Extract tenant id from request header

    Example:
    X-Tenant-ID: 1
    """
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant ID header missing",
        )
    return x_tenant_id