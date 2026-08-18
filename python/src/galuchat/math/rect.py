from typing import Generic,TypeVar,Tuple,Iterable,Collection,List,Union,Optional
import math
from abc import ABC,abstractmethod
from dataclasses import dataclass

T=TypeVar("T", int, float)
B=TypeVar("B",bound="BaseRect")

@dataclass(frozen=True)
class BaseRect(Generic[T],ABC):
    """ 基準点と高さ幅を持つボックスです。
        派生クラスはイミュータブルクラスとしてください。
        範囲は[x,x+width),[y,y+height)です。
    """
    x:T
    y:T
    width:T
    height:T
    # def __init__(self,x:T,y:T,w:T,h:T):
    #     self.x=x
    #     self.y=y
    #     self.width=w
    #     self.height=h
    @property
    def area(self)->T:
        return self.width*self.height
    @property
    def x2(self)->T:
        return self.x+self.width
    @property
    def y2(self)->T:
        return self.y+self.height    
    @property
    def cx(self)->float:
        return self.x+self.width/2
    @property
    def cy(self)->float:
        return self.y+self.height/2   
    
    def __str__(self)->str:
        return f"{self.x},{self.y},{self.width},{self.height}"
    def _cross(self,area:"BaseRect[T]")->Optional[Tuple[T,T,T,T]]:
        # 交差する領域の左、右、上、下の座標を計算ここでのltrbは内部的な表現
        left = max(self.x, area.x)
        right = min(self.x+self.width, area.x+area.width)
        top = max(self.y, area.y)
        bottom = min(self.y+self.height, area.y+area.height)
        
        # 交差が存在するかをチェック
        if left < right and top < bottom:
            return left, top, right-left, bottom-top
        else:
            return None  # 交差しない場合は None を返す
    @classmethod
    def _marge(cls,areas:List["BaseRect[T]"])->Tuple[T,T,T,T]:
        """ 矩形を統合して新しいxywhを返す。
        """
        assert(len(areas)>0)
        #ここでのLTRBは内部的なもの
        l=areas[0].x
        t=areas[0].y
        r=areas[0].x+areas[0].width
        b=areas[0].y+areas[0].height
        for a in areas[1:]:
            l=min(l,a.x)
            t=min(t,a.y)
            r=max(r,a.x+a.width)
            b=max(b,a.y+a.height)
        return (l,t,r-l,b-t)


    def isInside(self,x:T,y:T)->bool:
        """ ポイントが範囲内であるかを返す
        """
        return self.x<=x and x<(self.x+self.width) and self.y<=y and y<(self.y+self.height)
    def isInsideArea(self,area:"Rect[T]")->bool:
        """ areaが完全にselfの内部にあるかを返す。
        """
        return self.x<=area.x and self.y<=area.y and (area.y+area.height)<(self.y+self.height) and (area.x+area.width)<(self.x+self.width)
    @abstractmethod
    def cross(self,area:B)->Optional[B]:
        ...
    @abstractmethod
    def move(self,mx:T,my:T)->B:
        ...

 


@dataclass(frozen=True)
class GisRect(Generic[T],BaseRect[T]):
    """ 第一象限RECT
        経度、緯度を格納する。0度を基準として百分率。
    """
    # def __init__(self,x:T,y:T,w:T,h:T):
    #     super().__init__(x,y,w,h)
    @classmethod
    def createWithNSEW(cls,north:T,south:T,east:T,west:T)->"GisRect[T]":
        """ 北緯、南緯、東経、西経からジオイド表面の矩形を定義します。
        """
        assert(north>=south and east>=west)
        return GisRect[T](west,south,east-west,north-south)
    @classmethod
    def marge(cls,areas:List["GisRect[T]"])->"GisRect[T]":
        v=BaseRect[T]._marge(areas)
        return cls(v[0],v[1],v[2],v[3])
    
    def cross(self,area:"GisRect[T]")->Optional["GisRect[T]"]:
        r=self._cross(area)
        return None if r is None else GisRect[T](r[0],r[1],r[2],r[3])
    def move(self,mx:T,my:T)->"GisRect[T]":
        return GisRect[T](self.x+mx,self.y+my,self.width,self.height)
    def toInt(self,munit_x:float=1,munit_y:float=1)->"GisRect[int]":
        """ float型のインスタンスをmunitを積算してint型に変換します。
        """
        return GisRect[int](
            round(self.x*munit_x),
            round(self.y*munit_y),
            round(self.width*munit_x),
            round(self.height*munit_y)
        )
    def toFloat(self,munit:float=1.)->"GisRect[float]":
        """ float型のインスタンスをmunitを積算してfloat型に変換します。
        """
        return GisRect[float](
            self.x*munit,
            self.y*munit,
            self.width*munit,
            self.height*munit
        )

    @property
    def north(self)->T:
        return self.y+self.height
    @property
    def south(self)->T:
        return self.y
    @property
    def east(self)->T:
        return self.x+self.width
    @property
    def west(self)->T:
        return self.x

@dataclass(frozen=True)
class Rect(Generic[T],BaseRect[T]):
    """ [left,right),[top,bottom)のボックスを定義します。
        このクラスでは方向を定義しません。
    """
    # def __init__(self,x:T,y:T,w:T,h:T):
    #     super().__init__(x,y,w,h)

    @classmethod
    def marge(cls,areas:List["Rect[T]"])->"Rect[T]":
        v=cls._marge(areas)
        return cls(v[0],v[1],v[2],v[3])
    def cross(self,area:"Rect[T]")->Optional["Rect[T]"]:
        r=self._cross(area)
        return None if r is None else Rect[T](r[0],r[1],r[2],r[3])
    def move(self,mx:T,my:T)->"Rect[T]":
        return Rect[T](self.x+mx,self.y+my,self.width,self.height)
    def toInt(self,munit:float=1)->"Rect[int]":
        """ float型のインスタンスをmunitを積算してint型に変換します。
        """
        return Rect[int](
            round(self.x*munit),
            round(self.y*munit),
            round(self.width*munit),
            round(self.height*munit)
        )    






