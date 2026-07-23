# -*- coding: utf-8 -*-
"""
===================================
自选股相关响应模型
===================================

职责：
1. 定义默认自选股清单接口的响应模型
"""

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class WatchlistItemSchema(BaseModel):
    """单只自选股条目"""

    code: str = Field(..., description="股票代码", json_schema_extra={"example": "SH600519"})
    name: str = Field(..., description="股票名称", json_schema_extra={"example": "贵州茅台"})
    market: str = Field(..., description="所属市场", json_schema_extra={"example": "SH"})
    group: str = Field(..., description="分组名称", json_schema_extra={"example": "消费"})


class WatchlistSummaryResponse(BaseModel):
    """默认自选股清单汇总响应"""

    total: int = Field(..., description="自选股总数", json_schema_extra={"example": 5})
    groups: List[str] = Field(..., description="去重后的分组列表")
    items: List[WatchlistItemSchema] = Field(..., description="自选股条目明细")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total": 2,
            "groups": ["消费", "金融"],
            "items": [
                {"code": "SH600519", "name": "贵州茅台", "market": "SH", "group": "消费"},
                {"code": "SH601318", "name": "中国平安", "market": "SH", "group": "金融"},
            ],
        }
    })
