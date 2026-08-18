from typing import Sequence

from galuchat.io import ABytesReader, BytesBufferReader, BytesWriter
from galuchat.math.raster import IReadableRaster, IWritableRaster
from .BaseNode import BasePalletDataNode


class RawPalletNode(BasePalletDataNode):
    """ RawCodecのバイトイメージを格納する。
    """
    _data:bytes
    def __init__(self,resolution:int,data:bytes,pallet:Sequence[int]):
        assert (len(pallet)<=16)
        super().__init__(resolution,pallet)
        self._data=data
    @classmethod
    def parseRaster(cls,src:IReadableRaster,pallet:Sequence[int]):
        """ vsetをパレットとしてインスタンスを生成する。
            include_palletはバイトイメージに含めるか
        """
        assert (src.width*src.height%8==0 and src.width==src.height)
        assert (len(pallet)<=16)
        bw=BytesWriter()
        bw.writeSubByteWithMap(src.toArray(),pallet)
        return cls(src.width,bw.buffer,pallet)
    def getBytes(self):
        return self._data
    def toRaster(self,dest:IWritableRaster,x:int=0,y:int=0):
        src=BytesBufferReader(self._data)
        pixels=self.resolution**2
        nbits=ABytesReader.toBitWidth(len(self.pallet))
        frame_bits=(pixels*nbits+7)//8*8
        values=src.readSubBytesWithMap(frame_bits//nbits,self.pallet)
        for i,v in enumerate(values[:pixels]):
            dest.set(x+i%self.resolution,y+i//self.resolution,v)

