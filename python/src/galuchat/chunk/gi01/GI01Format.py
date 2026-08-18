CHUNK_NAME = b"GI01"

CC_RAW = 0
CC_RAWS = 1
CC_LZSS = 2


class BlockHeader:
    """GI01ブロックの圧縮方式とパレット差分方式を示す1バイトヘッダ。"""

    def __init__(self, byte1: int):
        assert 0 <= byte1 <= 0xff
        if byte1 & 0x4f:
            raise ValueError("invalid GI01 BlockHeader reserved bits")
        if ((byte1 >> 4) & 0x03) == 3:
            raise ValueError("reserved GI01 block compression type")
        self.byte1 = byte1

    @classmethod
    def create(cls, compression_type: int, palette_delta: bool) -> "BlockHeader":
        assert 0 <= compression_type <= 2
        return cls(((1 if palette_delta else 0) << 7) | (compression_type << 4))

    @property
    def compressionType(self) -> int:
        return (self.byte1 >> 4) & 0x03

    @property
    def paletteDelta(self) -> bool:
        return (self.byte1 & 0x80) != 0
