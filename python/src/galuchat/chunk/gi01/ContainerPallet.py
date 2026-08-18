from typing import Sequence

from .CellHeader import CellHeader


class ContainerPallet:
    """ContainerNodeの4要素を保持する2bit PalletMask。

    ContainerType=MIXEDではindex 3を子ノードの印として扱う。
    ContainerType=VALUESではindex 0～3をすべてパレット参照として扱う。
    """

    def __init__(
        self,
        mask: int,
        container_type: int,
        pallet: Sequence[int],
    ):
        assert 0 <= mask <= 0xff
        assert container_type in (
            CellHeader.CONTAINER_TYPE_MIXED,
            CellHeader.CONTAINER_TYPE_VALUES,
        )
        assert len(pallet) >= 4
        self.mask = mask
        self.containerType = container_type
        self._pallet = pallet

    def palletIndex(self, child_index: int) -> int | None:
        assert 0 <= child_index < 4
        index = (self.mask >> ((3 - child_index) * 2)) & 0x03
        if (
            self.containerType == CellHeader.CONTAINER_TYPE_MIXED
            and index == 3
        ):
            return None
        return index

    def palletValue(self, child_index: int) -> int | None:
        index = self.palletIndex(child_index)
        return None if index is None else self._pallet[index]

    @classmethod
    def create(
        cls,
        values4: Sequence[int | None],
        container_type: int,
    ) -> tuple["ContainerPallet", list[int]]:
        assert len(values4) == 4
        values = sorted({value for value in values4 if value is not None})
        if container_type == CellHeader.CONTAINER_TYPE_MIXED:
            assert any(value is None for value in values4)
            assert len(values) <= 3
        elif container_type == CellHeader.CONTAINER_TYPE_VALUES:
            assert all(value is not None for value in values4)
            assert len(values) <= 4
        else:
            raise ValueError("PalletMask is only valid for MIXED or VALUES ContainerType")

        mask = 0
        for value in values4:
            mask <<= 2
            if value is None:
                mask |= 3
            else:
                mask |= values.index(value)
        padded = values + [0] * (4 - len(values))
        return cls(mask, container_type, padded), values

    @classmethod
    def restore(
        cls,
        mask: int,
        container_type: int,
        pallet: Sequence[int],
    ) -> "ContainerPallet":
        return cls(mask, container_type, pallet)
