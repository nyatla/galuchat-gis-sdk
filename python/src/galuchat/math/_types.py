from typing import Tuple,TypeVar,Generic
from .rect import Rect

T=TypeVar("T", int, float)

class Point(Generic[T]):
    def __init__(self,x:T,y:T):
        self.x=x
        self.y=y

class BoundsData:
    """ Raster分析結果を格納する型です。
       領域を占める値について、存在するエリア、重心、合計ピクセル数を格納します。
    """
    def __init__(self,value:int,bounds:Rect[int],center:Tuple[int,int],sumarea:int):
        self.value=value
        self.bounds=bounds
        self.center=Point[int](center[0],center[1])
        self.sumarea=sumarea