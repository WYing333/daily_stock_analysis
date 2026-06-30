# -*- coding: utf-8 -*-
"""
===================================
告警汇总服务
===================================

职责：
1. 提供轻量的告警分类汇总（不读库、不发网络请求）
2. 供仪表盘顶部的告警概览卡片使用
"""

from __future__ import annotations

from typing import Any, Dict, List

# 告警级别的展示顺序，从高到低
ALERT_LEVELS: List[str] = ["critical", "warning", "info"]


def build_alerts_summary() -> Dict[str, Any]:
    """构建告警概览汇总

    返回一个静态的告警分级统计，用于仪表盘概览卡片。
    该函数是纯函数：不访问数据库，也不发起任何网络请求。

    Returns:
        Dict[str, Any]: 包含各级别数量、总数以及级别顺序的字典
    """
    by_level: Dict[str, int] = {
        "critical": 0,
        "warning": 0,
        "info": 0,
    }
    total = sum(by_level.values())
    return {
        "total": total,
        "by_level": by_level,
        "levels": list(ALERT_LEVELS),
    }
