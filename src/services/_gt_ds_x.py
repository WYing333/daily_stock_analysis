"""GT P10: mutual-import cycle in the service layer -> DS flag; BC/FC clean."""
from src.services._gt_ds_y import ds_y


def ds_x():
    return ds_y() + 1
