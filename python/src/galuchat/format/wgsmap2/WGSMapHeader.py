""" wsmapは1つの世界座標系リージョンを格納するデータセットです。
    2つにチャンクを格納します。
    [WGSMapHeader]
    [GaluchatImageDataChunk]
"""
from dataclasses import dataclass, field,InitVar
from ...io import ABytesReader,BytesBufferReader,ABytesWriter,BytesWriter
from ...chunk import Chunk
from ..types import SamplingMode_CENTER_POINT,CoordinateSystem
import json
@dataclass(frozen=True)
class WGSMapHeader(Chunk):
    VERSION_1=b"WGSMap/1"
    VERSION_2=b"WGSMap/2"
    VERSION_3=b"WGSMap/3"
    CHUNK_NAME=b"GLCH"

    """ 世界座標系メタデータを格納する。
        NAME:   "GLCH"
        SIZE:   MUINT
        ----
        [PAYLOAD]

        *PAYLOAD:VERSION_1
        VERSION     BYTE[16]
        UNIT-INV    MUINT
        WEST    MINT
        SOUTH   MINT

        *PAYLOAD:VERSION_2/VERSION_3
        VERSION                  :BYTE[16]
        UNIT-INV_X  MUINT
        UNIT-INV_Y  MUINT
        WEST    MINT
        SOUTH   MINT
        METADATA:
            L:    MINT (OPTIONAL、無効の場合0)
            TEXT: BYTE[L]
        =======
        [GaluchatImageDataChunk]
    """
    unit_inv_x:int=field(init=False)
    unit_inv_y:int=field(init=False)
    west:int=field(init=False)
    south:int=field(init=False)
    metadata:str=field(init=False)
    src: InitVar[ABytesReader|None] = None
    def __post_init__(self,src:ABytesReader):
        super().__post_init__(src)
        assert(self.name==self.CHUNK_NAME)
        br=BytesBufferReader(self.data)
        v=br.readBytesAsBStr(16)
        if v==WGSMapHeader.VERSION_1:
            object.__setattr__(self,"unit_inv_x",br.readMbUInt())   #Invers-Unit
            object.__setattr__(self,"unit_inv_y",self.unit_inv_x)   #Invers-Unit
            object.__setattr__(self,"west",br.readMbInt())
            object.__setattr__(self,"south",br.readMbInt())
            object.__setattr__(self,"metadata",None)
        elif v in (WGSMapHeader.VERSION_2,WGSMapHeader.VERSION_3):
            object.__setattr__(self,"unit_inv_x",br.readMbUInt())   #Invers-Unit
            object.__setattr__(self,"unit_inv_y",br.readMbUInt())   #Invers-Unit
            object.__setattr__(self,"west",br.readMbInt())
            object.__setattr__(self,"south",br.readMbInt())
            len_metadata=br.readMbUInt()
            str_metadata=None if len_metadata==0 else br.readAsBytes(len_metadata).decode()
            object.__setattr__(self,"metadata",str_metadata)
        else:
            raise ValueError(f"Invalid version:'{v.decode()}'")
    @classmethod
    def unpack(cls,src:ABytesReader)->"WGSMapHeader":
        return WGSMapHeader(src)
    @classmethod
    def pack(cls,src:"WGSMapHeader",dest:ABytesWriter):
        return Chunk.pack(cls.CHUNK_NAME,src.data,dest)
    


    @classmethod
    def createNew(cls,unit_inv_x:int,unit_inv_y:int,left:int,top:int,metadata:str)->"WGSMapHeader":
        return cls.createNewWithVersion(cls.VERSION_2,unit_inv_x,unit_inv_y,left,top,metadata)

    @classmethod
    def createNew3(cls,unit_inv_x:int,unit_inv_y:int,left:int,top:int,metadata:str)->"WGSMapHeader":
        return cls.createNewWithVersion(cls.VERSION_3,unit_inv_x,unit_inv_y,left,top,metadata)

    @classmethod
    def createNewWithVersion(cls,version:bytes,unit_inv_x:int,unit_inv_y:int,left:int,top:int,metadata:str)->"WGSMapHeader":
        bw=BytesWriter()
        bw.writeBytesAsBStr(version,16)
        bw.writeMbUInt(unit_inv_x)
        bw.writeMbUInt(unit_inv_y)
        bw.writeMbInt(left)
        bw.writeMbInt(top)
        if metadata is None:
            bw.writeMbUInt(0)
        else:
            b=metadata.encode()
            bw.writeMbUInt(len(b))
            bw.writeBytes(b)

        data=bw.buffer
        bw2=BytesWriter()
        Chunk.pack(cls.CHUNK_NAME,data,bw2)
        return WGSMapHeader(BytesBufferReader(bw2.buffer))
