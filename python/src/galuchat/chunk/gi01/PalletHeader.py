from galuchat.io import ABytesReader,ABytesWriter


class PalletHeader:
    """GI01 RLE DataNodeのパレット制御ヘッダ。"""

    PALLET_MODE:int
    capacity:int

    @classmethod
    def create(
        cls,
        pallet_mode:int,
        update_control:int,
        initial_index:int|None,
        value_bits_add:int=0)->"PalletHeader":
        if pallet_mode==0:
            return PalletHeader2(update_control,initial_index,value_bits_add)
        if pallet_mode==1:
            return PalletHeader3(update_control,initial_index,value_bits_add)
        if pallet_mode==2:
            return PalletHeader5(update_control,initial_index,value_bits_add)
        if pallet_mode==3:
            return PalletHeader16(update_control,initial_index,value_bits_add)
        raise ValueError("invalid RLE pallet mode")

    @classmethod
    def readFrom(cls,src:ABytesReader,pallet_mode:int)->"PalletHeader":
        if pallet_mode==0:
            return PalletHeader2.fromBits(src.readBitsAsInt32(7))
        if pallet_mode==1:
            return PalletHeader3.fromBits(src.readBitsAsInt32(9))
        if pallet_mode==2:
            return PalletHeader5.fromBits(src.readBitsAsInt32(12))
        if pallet_mode==3:
            return PalletHeader16.fromBits(src.readBitsAsInt32(20))
        raise ValueError("invalid RLE pallet mode")

    def writeTo(self,dest:ABytesWriter)->None:
        raise NotImplementedError()

    @property
    def updateCount(self)->int:
        if self.updatePalletTable is None:
            raise NotImplementedError()
        return self.updatePalletTable.bit_count()

    @property
    def updatePalletTable(self)->int|None:
        raise NotImplementedError()

    @property
    def initialIndex(self)->int|None:
        raise NotImplementedError()

    @property
    def valueBitsAdd(self)->int:
        return 0


class PalletHeader2(PalletHeader):
    """P2: 7bit, InitialIndex(1) + UpdatePalletTable2(2) + EncodingParams2(4)。"""

    PALLET_MODE=0
    capacity=2

    def __init__(self,update_table:int,initial_index:int|None,encoding_params:int=0):
        if initial_index is None or not 0<=initial_index<2:
            raise ValueError("invalid P2 initial index")
        if not 0<=update_table<4:
            raise ValueError("invalid P2 update table")
        if not 0<=encoding_params<16:
            raise ValueError("invalid P2 encoding params")
        self._update_table=update_table
        self._initial_index=initial_index
        self._encoding_params=encoding_params

    @classmethod
    def fromBits(cls,bits:int)->"PalletHeader2":
        if not 0<=bits<128:
            raise ValueError("invalid P2 header bits")
        return cls((bits>>4)&0x03,bits>>6,bits&0x0f)

    @property
    def byte1(self)->int:
        return (self._initial_index<<6)|(self._update_table<<4)|self._encoding_params

    def writeTo(self,dest:ABytesWriter)->None:
        dest.writeBitsFromInt32(self.byte1,7)

    @property
    def updatePalletTable(self)->int:
        return self._update_table

    @property
    def initialIndex(self)->int:
        return self._initial_index

    @property
    def valueBitsAdd(self)->int:
        return self._encoding_params


class PalletHeader3(PalletHeader):
    """P3: 9bit, InitialIndex(2) + UpdatePalletTable3(3) + EncodingParams3(4)。"""

    PALLET_MODE=1
    capacity=3

    def __init__(self,update_table:int,initial_index:int|None,encoding_params:int=0):
        if initial_index is None or not 0<=initial_index<3:
            raise ValueError("invalid P3 initial index")
        if not 0<=update_table<8:
            raise ValueError("invalid P3 update table")
        if not 0<=encoding_params<16:
            raise ValueError("invalid P3 encoding params")
        self._update_table=update_table
        self._initial_index=initial_index
        self._encoding_params=encoding_params

    @classmethod
    def fromBits(cls,bits:int)->"PalletHeader3":
        if not 0<=bits<512:
            raise ValueError("invalid P3 header bits")
        return cls((bits>>4)&0x07,bits>>7,bits&0x0f)

    def writeTo(self,dest:ABytesWriter)->None:
        dest.writeBitsFromInt32(
            (self._initial_index<<7)|(self._update_table<<4)|self._encoding_params,9)

    @property
    def updatePalletTable(self)->int:
        return self._update_table

    @property
    def initialIndex(self)->int:
        return self._initial_index

    @property
    def valueBitsAdd(self)->int:
        return self._encoding_params


class PalletHeader5(PalletHeader):
    """P5: 12bit, InitialIndex(3) + UpdatePalletTable5(5) + EncodingParams5(4)。"""

    PALLET_MODE=2
    capacity=5

    def __init__(self,update_table:int,initial_index:int|None,encoding_params:int=0):
        if initial_index is None or not 0<=initial_index<5:
            raise ValueError("invalid P5 initial index")
        if not 0<=update_table<32:
            raise ValueError("invalid P5 update table")
        if not 0<=encoding_params<16:
            raise ValueError("invalid P5 encoding params")
        self._update_table=update_table
        self._initial_index=initial_index
        self._encoding_params=encoding_params

    @classmethod
    def fromBits(cls,bits:int)->"PalletHeader5":
        if not 0<=bits<4096:
            raise ValueError("invalid P5 header bits")
        return cls((bits>>4)&0x1f,bits>>9,bits&0x0f)

    def writeTo(self,dest:ABytesWriter)->None:
        dest.writeBitsFromInt32(
            (self._initial_index<<9)|(self._update_table<<4)|self._encoding_params,12)

    @property
    def updatePalletTable(self)->int:
        return self._update_table

    @property
    def initialIndex(self)->int:
        return self._initial_index

    @property
    def valueBitsAdd(self)->int:
        return self._encoding_params


class PalletHeader16(PalletHeader):
    """P16: 20bit, UpdatePalletTable16(16) + EncodingParams16(4)。"""

    PALLET_MODE=3
    capacity=16

    def __init__(self,update_table:int,initial_index:int|None=None,encoding_params:int=0):
        if initial_index is not None:
            raise ValueError("P16 header has no initial index")
        if not 0<=update_table<65536:
            raise ValueError("invalid P16 update table")
        if not 0<=encoding_params<16:
            raise ValueError("invalid P16 encoding params")
        self._update_table=update_table
        self._encoding_params=encoding_params

    @classmethod
    def fromBits(cls,bits:int)->"PalletHeader16":
        if not 0<=bits<(1<<20):
            raise ValueError("invalid P16 header bits")
        return cls(bits>>4,None,bits&0x0f)

    def writeTo(self,dest:ABytesWriter)->None:
        dest.writeBitsFromInt32((self._update_table<<4)|self._encoding_params,20)

    @property
    def updatePalletTable(self)->int:
        return self._update_table

    @property
    def initialIndex(self)->None:
        return None

    @property
    def valueBitsAdd(self)->int:
        return self._encoding_params
