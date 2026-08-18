"""Index mapping base classes."""

from abc import ABC, abstractmethod
from typing import Generator, Iterable, Iterator, Union


class IndexMap(ABC):
    """インデクスのマッピング/アンマッピング機能を提供します。

    mapは順方向、unmapは逆方向の座標変換を行います。
    クラスは状態を持ちません。map/unmapはMTセーフである必要があります。
    """

    def __init__(self, size: int):
        self._size = size

    def wrapIterator(self, src: Iterator[int], direction: bool) -> Generator[int, None, None]:
        size = self._size
        tmp = [next(src) for _ in range(size**2)]
        if direction:
            for i in range(size**2):
                yield tmp[self.map(i)]
        else:
            for i in range(size**2):
                yield tmp[self.unmap(i)]

    @abstractmethod
    def map(self, index: int):
        """順方向の変換を行う"""
        ...

    @abstractmethod
    def unmap(self, index: int):
        """逆方向の変換を行う"""
        ...

    def convert(self, src: Union[Iterable[int], Iterator[int], bytearray], direction: bool):
        if isinstance(src, bytearray):
            return bytearray(list(self.wrapIterator(iter(src), direction)))
        elif isinstance(src, Iterable):
            return list(self.wrapIterator(iter(src), direction))
        else:
            return list(self.wrapIterator(src, direction))
