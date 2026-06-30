# -*- coding: utf-8 -*-
"""
Shared data parsing and normalization helpers.
"""

import json
import re
from typing import Any, Dict, List, Optional

from data_provider.base import is_bse_code


_MODEL_PLACEHOLDER_VALUES = {"unknown", "error", "none", "null", "n/a"}


def normalize_model_used(value: Any) -> Optional[str]:
    """Normalize placeholder/empty model values to None."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.lower() in _MODEL_PLACEHOLDER_VALUES:
        return None
    return text


def parse_json_field(value: Any) -> Any:
    """Best-effort JSON parse for string values; passthrough for others."""
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError, ValueError):
            return value
    return value


def _non_empty_dict(value: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(value, dict):
        return None
    return value if value else None


def _normalize_belong_boards(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if name is None:
            continue
        name_text = str(name).strip()
        if not name_text:
            continue
        board = {"name": name_text}
        if item.get("code") is not None:
            code_text = str(item.get("code")).strip()
            if code_text:
                board["code"] = code_text
        if item.get("type") is not None:
            type_text = str(item.get("type")).strip()
            if type_text:
                board["type"] = type_text
        normalized.append(board)
    return normalized


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            if text.endswith("%"):
                text = text[:-1].strip()
            return float(text)
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_sector_ranking_items(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if name is None:
            continue
        name_text = str(name).strip()
        if not name_text:
            continue
        ranking_item: Dict[str, Any] = {"name": name_text}
        change_pct = _safe_float(item.get("change_pct"))
        if change_pct is not None:
            ranking_item["change_pct"] = change_pct
        normalized.append(ranking_item)
    return normalized


def _normalize_sector_rankings(value: Any) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    if not isinstance(value, dict):
        return None

    return {
        "top": _normalize_sector_ranking_items(value.get("top")),
        "bottom": _normalize_sector_ranking_items(value.get("bottom")),
    }


def _is_empty_value(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _deep_merge_dicts(*values: Any) -> Optional[Dict[str, Any]]:
    merged: Dict[str, Any] = {}
    has_value = False
    for value in values:
        obj = parse_json_field(value)
        if not isinstance(obj, dict):
            continue
        has_value = True
        for key, item in obj.items():
            if _is_empty_value(item):
                continue
            existing = merged.get(key)
            if isinstance(existing, dict) and isinstance(item, dict):
                nested = _deep_merge_dicts(existing, item)
                if nested:
                    merged[key] = nested
            else:
                merged[key] = item
    return merged if has_value else None


def extract_fundamental_context(
    context_snapshot: Any,
    fallback_fundamental_payload: Any = None,
) -> Optional[Dict[str, Any]]:
    """
    Resolve fundamental_context from context snapshot, with optional fallback payload.
    """
    fallback_obj = parse_json_field(fallback_fundamental_payload)
    top_level_fundamental = None
    enhanced_fundamental = None
    snapshot_obj = parse_json_field(context_snapshot)
    if isinstance(snapshot_obj, dict):
        enhanced = snapshot_obj.get("enhanced_context")
        if isinstance(enhanced, dict):
            fundamental = enhanced.get("fundamental_context")
            if isinstance(fundamental, dict):
                enhanced_fundamental = fundamental
        raw_top_level = snapshot_obj.get("fundamental_context")
        if isinstance(raw_top_level, dict):
            top_level_fundamental = raw_top_level

    return _deep_merge_dicts(
        fallback_obj,
        top_level_fundamental,
        enhanced_fundamental,
    )


def extract_realtime_detail_fields(context_snapshot: Any) -> Dict[str, Any]:
    """
    Extract stable realtime price/change fields from persisted context snapshots.

    Supports both the standard `enhanced_context.realtime` layout and the
    agent-mode top-level `realtime_quote` compatibility shape.
    """
    snapshot_obj = parse_json_field(context_snapshot)
    if not isinstance(snapshot_obj, dict):
        return {"current_price": None, "change_pct": None}

    current_price = None
    change_pct = None

    enhanced = snapshot_obj.get("enhanced_context")
    if isinstance(enhanced, dict):
        realtime = enhanced.get("realtime")
        if isinstance(realtime, dict):
            current_price = realtime.get("price")
            change_pct = realtime.get("change_pct")

    for field in ("realtime_quote_raw", "realtime_quote"):
        realtime_payload = snapshot_obj.get(field)
        if not isinstance(realtime_payload, dict):
            continue
        if current_price is None:
            current_price = realtime_payload.get("price")
        if change_pct is None:
            change_pct = realtime_payload.get("change_pct")
        if change_pct is None:
            change_pct = realtime_payload.get("pct_chg")

    return {
        "current_price": current_price,
        "change_pct": change_pct,
    }


def extract_fundamental_detail_fields(
    context_snapshot: Any,
    fallback_fundamental_payload: Any = None,
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Extract stable API-facing financial and dividend blocks from fundamental_context.
    """
    fundamental_ctx = extract_fundamental_context(
        context_snapshot=context_snapshot,
        fallback_fundamental_payload=fallback_fundamental_payload,
    )
    if not isinstance(fundamental_ctx, dict):
        return {"financial_report": None, "dividend_metrics": None}

    earnings_block = fundamental_ctx.get("earnings")
    earnings_data = earnings_block.get("data") if isinstance(earnings_block, dict) else None
    if not isinstance(earnings_data, dict):
        return {"financial_report": None, "dividend_metrics": None}

    financial_report = _non_empty_dict(earnings_data.get("financial_report"))
    dividend_metrics = _non_empty_dict(earnings_data.get("dividend"))
    return {
        "financial_report": financial_report,
        "dividend_metrics": dividend_metrics,
    }


def extract_board_detail_fields(
    context_snapshot: Any,
    fallback_fundamental_payload: Any = None,
) -> Dict[str, Any]:
    """
    Extract stable board detail fields from fundamental_context.
    """
    fundamental_ctx = extract_fundamental_context(
        context_snapshot=context_snapshot,
        fallback_fundamental_payload=fallback_fundamental_payload,
    )
    if not isinstance(fundamental_ctx, dict):
        return {"belong_boards": [], "sector_rankings": None}

    boards_block = fundamental_ctx.get("boards")
    sector_rankings = None
    if isinstance(boards_block, dict):
        boards_status = boards_block.get("status")
        if boards_status in {"ok", "partial"} or boards_status is None:
            sector_rankings = boards_block.get("data")
    return {
        "belong_boards": _normalize_belong_boards(fundamental_ctx.get("belong_boards")),
        "sector_rankings": _normalize_sector_rankings(sector_rankings),
    }


# ---------------------------------------------------------------------------
# Stock code helpers
# ---------------------------------------------------------------------------

# Known exchange prefixes (case-insensitive) and the digit lengths they accept.
# e.g. SH600519 -> 600519, HK00700 -> 00700
_PREFIX_DIGIT_LENS: dict = {
    "SH": (6,),
    "SZ": (6,),
    "SS": (6,),
    "BJ": (6,),
    "HK": (1, 2, 3, 4, 5),
}

_SUFFIX_DIGIT_LENS: dict = {
    ".SH": (6,),
    ".SZ": (6,),
    ".SS": (6,),
    ".BJ": (6,),
    ".HK": (1, 2, 3, 4, 5),
}


def _valid_exchange_code(exchange: str, base: str, digit_lens: tuple[int, ...]) -> bool:
    if not (base.isdigit() and len(base) in digit_lens):
        return False
    if exchange == "BJ":
        return is_bse_code(base)
    return True


def _strip_exchange_prefix(text: str) -> Optional[str]:
    """Strip leading exchange prefix (SH/SZ/HK etc.) and return the bare digits, or None."""
    for prefix, digit_lens in _PREFIX_DIGIT_LENS.items():
        if text.startswith(prefix):
            base = text[len(prefix):]
            if _valid_exchange_code(prefix, base, digit_lens):
                return base.zfill(5) if prefix == "HK" else base
    return None


def _strip_exchange_suffix(text: str) -> Optional[str]:
    """Strip exchange suffix (.SH/.SZ/.SS/.HK) and return normalized bare digits, or None."""
    for suffix, digit_lens in _SUFFIX_DIGIT_LENS.items():
        if text.endswith(suffix):
            base = text[: -len(suffix)].strip()
            exchange = suffix.lstrip(".")
            if _valid_exchange_code(exchange, base, digit_lens):
                return base.zfill(5) if suffix == ".HK" else base
    return None


def is_code_like(value: str) -> bool:
    """Check if string looks like a stock code (5-6 digits, 1-5 letters, or prefixed code)."""
    text = value.strip().upper()
    if not text:
        return False
    if text.isdigit() and len(text) in (5, 6):
        return True
    if _strip_exchange_suffix(text) is not None:
        return True
    if re.match(r"^[A-Z]{1,5}(?:\.(?:US|[A-Z]))?$", text):
        return True
    # Support exchange-prefixed codes: SH600519, SZ000001, BJ920493, HK00700
    if _strip_exchange_prefix(text) is not None:
        return True
    return False


def normalize_code(raw: str) -> Optional[str]:
    """Normalize and validate a single stock code.

    Supports:
    - Plain digit codes: 600519, 00700
    - Suffix format: 600519.SH, 600519.SZ, 920493.BJ, 00700.HK
    - Prefix format: SH600519, SZ000001, BJ920493, HK00700 (case-insensitive)
    - US ticker symbols: AAPL, TSLA
    """
    text = raw.strip().upper()
    if not text:
        return None
    if text.isdigit() and len(text) in (5, 6):
        return text
    if re.match(r"^[A-Z]{1,5}(?:\.(?:US|[A-Z]))?$", text):
        return text
    stripped_suffix = _strip_exchange_suffix(text)
    if stripped_suffix is not None:
        return stripped_suffix
    # Support exchange-prefixed codes: SH600519 -> 600519, BJ920493 -> 920493
    stripped = _strip_exchange_prefix(text)
    if stripped is not None:
        return stripped
    return None
