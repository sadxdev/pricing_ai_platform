import pytest


@pytest.mark.asyncio
async def test_list_products(client):
    res = await client.get("/v1/products/")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == 1
    assert data[0]["name"] == "Test Product"


@pytest.mark.asyncio
async def test_list_products_returns_correct_fields(client):
    res = await client.get("/v1/products/")
    assert res.status_code == 200
    product = res.json()[0]
    assert "id" in product
    assert "name" in product
    assert "sku" in product