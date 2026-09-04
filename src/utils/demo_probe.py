"""Self-contained demo util — no cross-layer import, imported by nothing.
All three metrics should read clean (a true-negative control)."""


def normalize_ratio(numerator: float, denominator: float) -> float:
    if not denominator:
        return 0.0
    return round(numerator / denominator, 4)
