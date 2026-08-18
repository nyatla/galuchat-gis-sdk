from typing import Sequence

from .IndexMap import IndexMap


class ChaindIndexMap(IndexMap):
    """複数のIndexmapを連続して適応します。"""

    def __init__(self, maps: Sequence[IndexMap]):
        super().__init__(maps[0]._size)
        self._maps = list(maps)
        self._unmaps = list(reversed(self._maps))

    def map(self, index: int) -> int:
        d = index
        for im in self._maps:
            d = im.map(d)
        return d

    def unmap(self, index: int) -> int:
        d = index
        for im in self._unmaps:
            d = im.unmap(d)
        return d
