from ._RlePalletNodeBase import RlePalletNodeBase


class RlePallet16Node(RlePalletNodeBase):
    """6値から16値の4bit直接index RLEを保持する。"""
    PALLET_MODE=3
    MIN_PALLET_SIZE=6
    MAX_PALLET_SIZE=16
