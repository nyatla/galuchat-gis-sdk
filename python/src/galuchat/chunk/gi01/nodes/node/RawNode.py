from galuchat.io import BytesBufferReader, BytesWriter
from galuchat.math.raster import IReadableRaster, IWritableRaster
from .BaseNode import BaseDataNode


class RawNode(BaseDataNode):
    """ RawCodecのバイトイメージを格納する。
    """
    _data:bytes
    def __init__(self,resolution:int,data:bytes):
        super().__init__(resolution)
        self._data=data
    @classmethod
    def parseRaster(cls,src:IReadableRaster):
        """ ビット幅調整を行わずにインスタンスを生成する。
        """
        assert (src.width*src.height%8==0 and src.width==src.height)
        bw=BytesWriter()
        bw.writeMbUInts(src.toArray())
        return cls(src.width,bw.buffer)
    def getBytes(self):
        return self._data
    def toRaster(self,dest:IWritableRaster,x:int=0,y:int=0):
        src=BytesBufferReader(self._data)
        for i in range(self.resolution**2):
            dest.set(x+i%self.resolution,y+i//self.resolution,src.readMbUInt())

