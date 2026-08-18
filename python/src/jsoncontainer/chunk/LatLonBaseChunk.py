
from typing import Iterable, Self,Sequence,Tuple,Any,ClassVar
from dataclasses import dataclass
from typing import Any
from ..JsonContainer import JsonContainer
from ..writer import IJsonable,CustomPrettyJsonType, Inline, RowObject

@dataclass
class LatLonBaseChunk(JsonContainer):
    @dataclass
    class UnitInv(IJsonable):
        FIELD:ClassVar[str]="unit-inv"
        x:int#lat
        y:int#lon
        @classmethod
        def parse(cls,src:Any)->Self:
            return cls(src["x"],src["y"])
        def toPrettyJson(self)->CustomPrettyJsonType:
            return Inline({"x":self.x,"y":self.y,})

    @dataclass
    class Bounds(IJsonable):
        FIELD:ClassVar[str]="bounds"
        lat:int
        lon:int
        lwidth:int
        lheight:int
        quadrant:int
        @classmethod
        def parse(cls,s:Any)->Self:
            q=int(s["quadrant"])
            if q<1 or q>4:
                raise RuntimeError()
            return cls(int(s["lat"]),int(s["lon"]),int(s["lwidth"]),int(s["lheight"]),q)
        def toPrettyJson(self)->CustomPrettyJsonType:
            return RowObject((
                (("lat",self.lat),("lon",self.lon),),
                (("lwidth",self.lwidth),("lheight",self.lheight)),
                (("quadrant",self.quadrant),))
            )
    @dataclass
    class Sampling(IJsonable):
        CS_WGS84:ClassVar[str]="WGS84"
        FIELD:ClassVar[str]="sampling"
        coordsystem:str
        sampling_params:str|None
        @classmethod
        def parse(cls,s:Any)->Self:
            return cls(s["coordsystem"],s["sampling_params"])
        def toPrettyJson(self)->CustomPrettyJsonType:
            return Inline({"coordsystem":self.coordsystem,"sampling_params":self.sampling_params})


    CHUNK_TYPE:ClassVar[str]="LatLonBase:1"
    units:UnitInv
    bounds:Bounds
    sampling:Sampling
    def toPrettyJson(self)->CustomPrettyJsonType:
        return {
            "type":self.CHUNK_TYPE,
            "unit-inv":self.units.toPrettyJson(),
            "bounds":self.bounds.toPrettyJson(),
            "sampling":self.sampling.toPrettyJson()
        }
    @classmethod
    def parse(cls,src:Any)->Self:
        if src["type"]!=cls.CHUNK_TYPE:
            raise RuntimeError()
        return cls(
            cls.UnitInv.parse(src["unit-inv"]),
            cls.Bounds.parse(src["bounds"]),
            cls.Sampling.parse(src["sampling"]))
