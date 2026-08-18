from abc import ABC,abstractmethod
from ..io import ABytesWriter,ABytesReader,MBIntDef
from typing import TypeVar,Generic
from dataclasses import dataclass, field,InitVar
T=TypeVar("T", bound="Chunk")

@dataclass(frozen=True)
class Chunk:
    """ チャンクのプロパティはdataに対するアクセサを持つことができるが、データを二重に持つことを防ぐため、メンバ変数に値を持つべきでない。
        パース済のデータは生成関数を介してオブジェクトを返すべきである。例外として、アクセス頻度の高い少量の値は許容する。
        完全にキャッシュを排除する場合は、ChunkReaderとして実装する事。
    """
    _name: bytes = field(init=False)
    _data: bytes = field(init=False, repr=False)
    src:InitVar[ABytesReader|None] = None
    def __post_init__(self, src: ABytesReader):
        object.__setattr__(self,"_name",src.readAsBytes(4))
        size = src.readMbUInt()
        object.__setattr__(self,"_data",src.readAsBytes(size))

    @property
    def name(self)->bytes:
        return self._name
    @property
    def size(self)->int:
        """ データブロックのサイズ
        """
        return len(self._data)
    @property
    def sizeOfChunk(self)->int:
        """ チャンク全体のサイズ
        """
        return MBIntDef.sizeOfMbUint(len(self._data))+len(self.name)+len(self.data)
    @property
    def data(self)->bytes:
        """ データブロック
        """
        return self._data
    
    @classmethod
    def unpack(cls,src:ABytesReader)->"Chunk":
        return Chunk(src)
    @classmethod
    def pack(cls,name:bytes,data:bytes,dest:ABytesWriter):
        dest.writeBytes(name)
        dest.writeMbUInt(len(data))
        dest.writeBytes(data)
        return
