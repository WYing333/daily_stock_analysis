# -*- coding: utf-8 -*-
"""
===================================
告警汇总接口
===================================

职责：
1. 提供 /api/v1/alerts-summary 告警概览接口
2. 返回各级别告警的轻量统计，供仪表盘概览卡片使用
"""

from typing import Any, Dict

from fastapi import APIRouter

from src.services.alerts_summary_service import build_alerts_summary

router = APIRouter()


@router.get("/summary")
async def get_alerts_summary() -> Dict[str, Any]:
    """获取告警概览汇总

    返回各级别告警数量及总数，用于仪表盘顶部的概览卡片。

    Returns:
        Dict[str, Any]: 告警分级统计
    """
    return build_alerts_summary()
