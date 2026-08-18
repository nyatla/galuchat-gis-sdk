from typing import Tuple,Iterable,Iterator,List,Generator,Generic,TypeVar
import math
from abc import ABC ,abstractmethod
from dataclasses import dataclass,InitVar,field
import itertools

T=TypeVar("T")
CLASSTYPE=TypeVar("CLASSTYPE",bound="ISegment")

class ISegment(Generic[CLASSTYPE,T],ABC):
    """ [始点,終点]のセグメントを返します。
    """
    @property
    @abstractmethod
    def size(self)->int:
        """ Segmentの長さを返す
        """
        ...
    @property
    @abstractmethod
    def center(self)->T:
        """ セグメントの中心を返す
        """
        ...


@dataclass(frozen=True)
class BaseSegment(ISegment[CLASSTYPE,T],ABC):
    """ [始点,終点]のセグメントを返します。
    """
    start:T
    end:T
    def __str__(self)->str:
        return f"{self.start},{self.end}"




@dataclass(frozen=True)
class FloatSegment(BaseSegment["FloatSegment",float]):
    """ 単純な[始点,終点]のセグメントを返します。
    """
    @classmethod
    def createInstance(cls,start:float,end:float):
        return FloatSegment(start,end)
    @property
    def size(self)->int:
        """ Segmentの長さを返す
        """
        return self.end-self.start
    @property
    def center(self)->float:
        """ セグメントの中心を返す
        """
        return (self.start+self.end)*0.5
    def split(self,max_unit:float)->Generator["FloatSegment", None, None]:
        """ セグメントを最大max_unitの長さづつ返します。
        """
        s=self.start
        e=self.end
        for i in range(math.ceil((e-s)/max_unit)):
            yield FloatSegment.createInstance(s+i*max_unit,min(e,s+(i+1)*max_unit))
    def __str__(self)->str:
        return f"{self.start},{self.end}"

@dataclass(frozen=True)
class GridSegment(BaseSegment["GridSegment",float]):
    """ start,endを包括するunit単位の線分です。
        インスタンスの生成はcreateInstanceを使います。
        unit単位の線分の中心がunit単位のグリッドになります。
        二次元座標系で格子の交点が領域の中心になる座標系に使います。
    """
    _start_index:int #開始インデクス位置
    _num_of_unit:int
    _unit_inv:int
    @classmethod
    def createInstance(cls,start:float,end:float,unit_inv:int)->"GridSegment":
        #unit単位のindex化
        start_index=math.floor((start*unit_inv)+0.5)
        end_index=math.ceil((end*unit_inv)-0.5)
        num_of_unit=end_index-start_index+1
        return GridSegment((start_index-0.5)/unit_inv,(start_index+num_of_unit-1.0+0.5)/unit_inv,start_index,num_of_unit,unit_inv)
        # return GridSegment((start_index-0.5)/unit_inv,(end_index+0.5)/unit_inv,start_index,num_of_unit,unit_inv)
    @property
    def start_index(self)->int:
        return self._start_index
    @property
    def end_index(self)->int:
        return self._start_index+self._num_of_unit-1

    @property
    def size(self)->int:
        """ Segmentの長さを返す
        """
        return self._num_of_unit/self._unit_inv
    @property
    def center(self)->float:
        """ セグメントの中心を返す
        """
        return (self._start_index*2+self._num_of_unit-1)*0.5/self._unit_inv
    @property
    def numOfUnit(self)->int:
        """ 内包するユニット数を返します。
        """
        return self._num_of_unit
    
    def getUnitSegment(self,idx:int,num_of_unit):
        """ セグメントをunitsize個のunits単位に分割して、先頭からidx個めを返します。
        """
        assert(idx<self.numOfUnit)
        unit_inv=self._unit_inv
        ssi=self._start_index
        esi=ssi+self._num_of_unit
        si=ssi+(idx*num_of_unit)
        ei=ssi+(idx+1)*num_of_unit
        if ei>esi:
            ei=esi
        return GridSegment((si-0.5)/unit_inv,(ei-0.5)/unit_inv,si,ei-si,unit_inv)

    def split(self,num_of_unit:int)->Generator["GridSegment", None, None]:
        """ セグメントをunitsize個のunits単位に分割して、先頭から順に返します。セグメントの境界はunit単位に揃えられます。
            返却するセグメントは、unit*unitsの長さを持つセグメントです。
        """
        unit_inv=self._unit_inv
        ssi=self._start_index
        esi=ssi+self._num_of_unit
        nofi=(self.numOfUnit+num_of_unit-1)//num_of_unit
        for i in range(nofi):
            si=ssi+(i*num_of_unit)
            ei=ssi+(i+1)*num_of_unit
            if ei>esi:
                ei=esi
            yield GridSegment((si-0.5)/unit_inv,(ei-0.5)/unit_inv,si,ei-si,unit_inv)



