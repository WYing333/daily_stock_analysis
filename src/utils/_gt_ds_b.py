"""GT P3: mutual-import cycle (same layer) -> DS flag; BC/FC clean."""
from src.utils._gt_ds_a import ds_a


def ds_b():
    return 1
