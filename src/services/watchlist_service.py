# -*- coding: utf-8 -*-
"""
===================================
默认自选股清单服务
===================================

职责：
1. 提供一份内置的默认自选股清单（无数据库、无网络依赖）
2. 汇总分组与数量等只读统计信息

说明：
    该清单为静态内置数据，主要用于在尚未配置个人自选股时
    向前端提供一个可展示的默认观察列表。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class WatchlistItem:
    """单只自选股条目"""

    code: str
    name: str
    market: str
    group: str


# 内置默认自选股清单（静态数据，不可变）
_DEFAULT_WATCHLIST: tuple[WatchlistItem, ...] = (
    WatchlistItem(code="SH600519", name="贵州茅台", market="SH", group="消费"),
    WatchlistItem(code="SZ000858", name="五粮液", market="SZ", group="消费"),
    WatchlistItem(code="SH601318", name="中国平安", market="SH", group="金融"),
    WatchlistItem(code="SZ300750", name="宁德时代", market="SZ", group="新能源"),
    WatchlistItem(code="HK00700", name="腾讯控股", market="HK", group="科技"),
)


class WatchlistService:
    """默认自选股清单只读服务"""

    def __init__(self, items: tuple[WatchlistItem, ...] = _DEFAULT_WATCHLIST) -> None:
        self._items = items

    def list_items(self) -> List[WatchlistItem]:
        """
        返回默认自选股清单

        Returns:
            List[WatchlistItem]: 自选股条目列表
        """
        return list(self._items)

    def list_groups(self) -> List[str]:
        """
        返回去重后的分组名称（按首次出现顺序）

        Returns:
            List[str]: 分组名称列表
        """
        seen: List[str] = []
        for item in self._items:
            if item.group not in seen:
                seen.append(item.group)
        return seen

    def summary(self) -> dict:
        """
        汇总自选股清单的只读统计信息

        Returns:
            dict: 包含总数、分组列表以及条目明细
        """
        return {
            "total": len(self._items),
            "groups": self.list_groups(),
            "items": [
                {
                    "code": item.code,
                    "name": item.name,
                    "market": item.market,
                    "group": item.group,
                }
                for item in self._items
            ],
        }
