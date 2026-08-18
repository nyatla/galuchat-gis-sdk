from ._RlePalletNodeBase import RlePalletNodeBase


class RlePallet3Node(RlePalletNodeBase):
    """3値の1bit差分RLEを保持する。"""
    PALLET_MODE=1
    MIN_PALLET_SIZE=3
    MAX_PALLET_SIZE=3
