"""GT: mutual-import cycle (same package) -> DS flag; BC/FC clean."""
from src.core._gt_ds_q import ds_q


def ds_p():
    return ds_q() + 1
