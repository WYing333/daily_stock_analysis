"""GT P3: mutual-import cycle (same layer) -> DS flag; BC/FC clean."""
from src.utils._gt_ds_b import ds_b


def ds_a():
    return ds_b() + 1
