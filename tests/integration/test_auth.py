import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_request_without_token_returns_401():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        res = await ac.get("/v1/products/")
        assert res.status_code in [401, 403]


@pytest.mark.asyncio
async def test_request_with_valid_token_returns_200(client):
    res = await client.get("/v1/products/")
    assert res.status_code == 200