from fastapi import Header, HTTPException


async def get_tenant_id(x_tenant_id: int = Header(...)) -> int:
    """
    Extract tenant_id from request header

    Required Header:
    X-Tenant-ID: <int>
    """

    if not x_tenant_id:
        raise HTTPException(
            status_code=400,
            detail="X-Tenant-ID header is required"
        )

    return x_tenant_id