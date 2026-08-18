from ._RlePalletNodeBase import RlePalletNodeBase


class RlePallet5Node(RlePalletNodeBase):
    """4値または5値の2bit差分RLEを保持する。"""
    PALLET_MODE=2
    MIN_PALLET_SIZE=4
    MAX_PALLET_SIZE=5
