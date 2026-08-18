from abc import ABC,abstractmethod
from typing import Self,Any

from .CustomPrettyWriter import CustomPrettyJsonType

class IJsonable(ABC):
    @classmethod
    @abstractmethod
    def parse(cls,src:Any)->Self:
        ...
    @abstractmethod
    def toPrettyJson(self)->CustomPrettyJsonType:
        ...    
