from ._RlePalletNodeBase import RlePalletNodeBase


class RlePallet2Node(RlePalletNodeBase):
    """1値または2値の交互RLEを保持する。"""
    PALLET_MODE=0
    MIN_PALLET_SIZE=1
    MAX_PALLET_SIZE=2
