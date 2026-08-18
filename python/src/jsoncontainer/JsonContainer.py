from abc import ABC,abstractmethod
from typing import Self,Any,ClassVar, TextIO
from dataclasses import dataclass,field
import json

from .writer import IJsonable,CustomPrettyWriter

@dataclass
class JsonContainer(IJsonable,ABC):
    @dataclass
    class ContainerType:
        name:str
        version:int
        subname:str|None
        @classmethod
        def parse(cls,src:str)->Self:
            ss=src.split(":")
            l=len(ss)
            if l==2:
                return cls(ss[0],int(ss[1]),None)
            if l==4:
                return cls(ss[0],int(ss[1]),ss[3])
            raise RuntimeError(f"Invalid type format `{src}`")
        def __str__(self):
            return f"{self.name}:{self.version}"+("" if self.subname is None else f"::{self.subname}") 
    CHUNK_TYPE: ClassVar[str]
    container_type:ContainerType=field(init=False)
    def __post_init__(self):
        self.container_type=self.CHUNK_TYPE
    def __init_subclass__(cls):
        super().__init_subclass__()
        if "CHUNK_TYPE" not in cls.__dict__:
            raise TypeError(
                f"{cls.__name__} must define CHUNK_TYPE"
            )
    def dumps(self) -> str:
            return CustomPrettyWriter().dumps(self.toPrettyJson())

    def dump(self, fp: TextIO) -> None:
        fp.write(self.dumps())

    @classmethod
    def loads(cls, text: str) -> Self:
        return cls.parse(json.loads(text))

    @classmethod
    def load(cls, fp: TextIO) -> Self:
        return cls.loads(fp.read())