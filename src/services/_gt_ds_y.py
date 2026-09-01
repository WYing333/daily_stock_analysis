"""GT P10: mutual-import cycle in the service layer -> DS flag; BC/FC clean."""
from src.services._gt_ds_x import ds_x


def ds_y():
    return 1
