from __future__ import annotations

from app.core.dependencies import get_home_service
from fastapi import APIRouter, Depends

from .schemas import HomeDashboardResponse
from .service import HomeService


router = APIRouter(
    prefix="/api/home",
    tags=["首页"],
)

@router.get(
    "/dashboard",
    response_model=HomeDashboardResponse,
    summary="获取首页宏观数据看板",
)
async def get_dashboard(
    service: HomeService = Depends(
        get_home_service
    )
) -> HomeDashboardResponse:

    data = await service.get_dashboard()

    return HomeDashboardResponse(
        code=0,
        message="success",
        data=data,
    )