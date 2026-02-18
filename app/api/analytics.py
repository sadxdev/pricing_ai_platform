from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/revenue")
async def get_total_revenue():
    # TODO: replace with real DB aggregation
    return {
        "total": 120000,
        "timeseries": [
            {"date": "2026-02-01", "revenue": 10000},
            {"date": "2026-02-02", "revenue": 12000},
        ],
    }
