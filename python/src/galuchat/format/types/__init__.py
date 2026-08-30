""" formatに格納する特別値型の定義

"""
from enum import Enum
from typing import Optional



class CoordinateSystem(Enum):
    """ 座標系の種類
    """
    BITMAP=1 #数値系
    WGS84=2   #WGS84系
    @classmethod
    def parse(cls,v:str)->Optional["CoordinateSystem"]:
        """ 文字列から値を得る
        """
        try:
            # Enumの名前を使用して文字列と一致させる
            return cls[v]
        except KeyError:
            # 無効な文字列が渡された場合、エラーを発生させる
            raise RuntimeError(f"Invalid CoordinateSystem: {v}")

import json
from dataclasses import dataclass,field
from abc import ABC,abstractmethod




@dataclass(frozen=True)
class SamplingMode(ABC):
    value: int
    @abstractmethod
    def toJsonObject(self) -> object:
        ...
    def toJsonText(self) -> str:
        return json.dumps(self.toJsonObject())

@dataclass(frozen=True)
class SamplingMode_CENTER_POINT(SamplingMode):
    # クラス変数の定義
    NAME:str = field(init=False, default="CENTER_POINT")     
    def __init__(self):
        super().__init__(value=1)
    def toJsonObject(self) -> object:
        return [self.NAME]

@dataclass(frozen=True)
class SamplingMode_MAX_AREA(SamplingMode):
    NAME:str = field(init=False, default="MAX_AREA")     
    minimum_rate: float

    def __init__(self, minimum_rate: float):
        super().__init__(value=2)
        object.__setattr__(self, "minimum_rate", minimum_rate)
    def toJsonObject(self) -> object:
        return [self.NAME,{"minimum_rate":self.minimum_rate}]


class SamplingModeBuilder:
    @classmethod
    def parseArgs(cls,args)->SamplingMode:
        if args.sampling==SamplingMode_CENTER_POINT.NAME:
            assert(args.minimum_rate is None)
            return SamplingMode_CENTER_POINT()
        elif args.sampling==SamplingMode_MAX_AREA.NAME:
            return SamplingMode_MAX_AREA(0 if args.minimum_rate is None else args.minimum_rate)
        else:
            raise RuntimeError()
    @classmethod
    def parseJson(cls,jsonstr:str)->SamplingMode:
        j=json.loads(jsonstr)
        if j[0]==SamplingMode_CENTER_POINT.NAME:
            return SamplingMode_CENTER_POINT()
        elif j[0]==SamplingMode_MAX_AREA.NAME:
            return SamplingMode_MAX_AREA(j[1]["minimum_rate"])
        else:
            raise RuntimeError()
