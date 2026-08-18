from typing import List,TypeVar,Generic,Set,Sequence
from abc import ABC,abstractmethod
from ..rect import Rect
from .._types import BoundsData




class IBaseRaster(ABC):
    @property
    def width(self):
        ...
    @property
    def height(self):
        ...        
    @property
    def numOfPixels(self):
        """ピクセル数を返す
        """
        ...
    

T_READABLERASTER_DEST=TypeVar("T_READABLERASTER_DEST",bound="IReadableRaster")
class IReadableRaster(IBaseRaster,Generic[T_READABLERASTER_DEST],ABC):
    """ 読み取り専用のRaster
        Rasterを返す場合、それぞれのバッファメモリは独立していなければならない。
    """
    # def __init__(self,w:int,h:int):
    #     super().__init__(w,h)
    @abstractmethod
    def get(self,x:int,y:int)->int:
        """ 値を取得する
        """
        ...
    @abstractmethod
    def createSubRaster(self,x:int,y:int,w:int,h:int)->T_READABLERASTER_DEST:
        """ 新たにサブラスタを生成する。
        """
        ...
    @abstractmethod
    def padding(self,left:int,top:int,right:int,bottom:int,pad:int)->T_READABLERASTER_DEST:
        """ 新たにパディングしたラスタを生成する。
        """
    @abstractmethod
    def toArray(self)->Sequence[int]:
        """00->01->10->11の順で直列化した配列を返します。
        """
        ...
    @abstractmethod
    def getBoundsList(self)->Sequence[BoundsData]:
        """ Rasterから値毎の面積、重心、Boundsセットを得る
        """        
        ...
    @abstractmethod
    def valueSet(self,range:Rect[int]=None)->Set[int]:
        """ Rasterを構成する値セットを返します。
        """
        ...


class IWritableRaster(IReadableRaster[T_READABLERASTER_DEST],Generic[T_READABLERASTER_DEST],ABC):
    # def __init__(self,w:int,h:int):
    #     super().__init__(w,h)
    @abstractmethod
    def set(self,x:int,y:int,v:int):
        """ 値をセットする
        """
        ...

T_READABLERASTER_DEST=TypeVar("T_READABLERASTER_DEST",bound="IReadableRaster")

class Raster(Generic[T_READABLERASTER_DEST],IWritableRaster[T_READABLERASTER_DEST],ABC):
    _width:int
    _height:int
    def __init__(self,width:int,height:int):
        self._width=width
        self._height=height
        # self._buf=buf
    def __eq__(self,v:object)->bool:
        if not isinstance(v,Raster):
            return False
        if self.width!=v.width or self.height!=v.height:
            return False
        return v.toArray()==self.toArray()
    @property
    def width(self):
        return self._width
    @property
    def height(self):
        return self._height        
    @property
    def numOfPixels(self):
        return self.width*self.height



    def getBoundsList(self)->Sequence[BoundsData]:
        """ Rasterから値毎の面積、重心、Boundsセットを得る
        """
        tbl={}
        for y in range(self.height):
            for x in range(self.width):
                p=self.get(x,y)
                if p not in tbl:
                    #count,vsum,hsum,xmax,ymax,xmin,ymin
                    tbl[p]=[1,x,y,x,y,x,y]
                else:
                    n=tbl[p]
                    tbl[p]=[n[0]+1,n[1]+x,n[2]+y,max(n[3],x),max(n[4],y),min(n[5],x),min(n[6],y)]
        ret:List[BoundsData]=[]
        for k,v in tbl.items():
            ret.append(BoundsData(k,Rect[int](v[5],v[6],v[3]-v[5],v[4]-v[6]),(v[1]//v[0],v[2]//v[0]),v[0]))
        return ret  #面積、重心、Bounds

    def toSquareUnitRaster(self,unit:int,pad:int)->List["T_READABLERASTER_DEST"]:
        """ ラスタをunit単位四方にして、グリッドを00->01->10->11順に直列化する。
            一度大きいラスタを生成するから効率悪いよ。
        """
        pad_r=((self.width+unit-1)//unit)*unit-self.width
        pad_b=((self.height+unit-1)//unit)*unit-self.height
        
        sur=self.padding(0,0,pad_r,pad_b,pad) #パディングしたラスタを生成
        assert(sur.height%unit==0 and sur.width%unit==0)
        yn=sur.height//unit
        xn=sur.width//unit
        r=[]
        for y in range(yn):
            for x in range(xn):
                r.append(sur.createSubRaster(x*unit,y*unit,unit,unit))
        return r

