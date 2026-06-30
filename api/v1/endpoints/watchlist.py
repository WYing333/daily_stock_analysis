# -*- coding: utf-8 -*-
"""
===================================
默认自选股清单接口
===================================

职责：
1. 提供 /api/v1/watchlist/summary 只读接口
2. 返回内置的默认自选股清单及其分组统计
"""

from fastapi import APIRouter

from api.v1.schemas.watchlist import WatchlistSummaryResponse
from src.services.watchlist_service import WatchlistService

router = APIRouter()


@router.get("/summary", response_model=WatchlistSummaryResponse)
async def watchlist_summary() -> WatchlistSummaryResponse:
    """
    默认自选股清单汇总接口

    返回内置的默认自选股清单、分组列表以及总数，
    无需数据库或网络依赖，可用于前端默认展示。

    Returns:
        WatchlistSummaryResponse: 包含总数、分组与条目明细
    """
    service = WatchlistService()
    return WatchlistSummaryResponse(**service.summary())
