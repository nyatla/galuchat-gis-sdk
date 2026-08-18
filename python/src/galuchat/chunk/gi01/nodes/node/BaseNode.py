from typing import Sequence
from abc import ABC,abstractmethod

from galuchat.math.raster import IWritableRaster


class BaseNode(ABC):
    """ ノード情報格納のベースクラス
    """
    _resolution:int
    def __init__(self,resolution:int):
        self._resolution=resolution
    @property
    def resolution(self)->int:
        return self._resolution
    @abstractmethod
    def toRaster(self,dest:IWritableRaster,x:int=0,y:int=0):
        ...

class BaseDataNode(BaseNode,ABC):
    @abstractmethod
    def getBytes(self):
        ...

class BasePalletDataNode(BaseDataNode,ABC):
    """ パレットノード
    """
    _pallet:Sequence[int]
    def __init__(self,resolution:int,pallet:Sequence[int]):
        super().__init__(resolution)
        self._pallet=pallet
    @property
    def pallet(self)->Sequence[int]:
        """ パレット値
        """
        return self._pallet

