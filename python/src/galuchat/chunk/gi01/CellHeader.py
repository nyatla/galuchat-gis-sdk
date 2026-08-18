from typing import Union,Dict,List,Tuple,Sequence,Iterator,Optional
from ...math import toBitWidth
from enum import Enum
#%%

class CellHeader:
    """
    7-6 TYPE
    TYPE==0 ContainerNode
        5-4 ContainerType
            0   Mixed
            1   Values
            2   Mono value
            3   Reserved
        3-0 UpdatePalletTable4
    TYPE==1 RAW
        5-4 Pallet-Resolution
            0   1bit
            1   2bit
            2   4bit
            3   8bit+
        3-0 UpdatePalletTableLow4
    TYPE==2 RLE
        5-4 Pallet-Resolution
            0   1bit
            1   2bit
            2   4bit
            3   8bit+
        3-2 DataEncoding
            0   MBUInt
            1   ShortValue
            2   SingleEdgeRow
            3   Reserved
        1-0 ScanMode
            0   Zigzag
            1   MirrorH -> Zigzag
            2   Zigzag -> Transpose
            3   MirrorV -> Zigzag -> Transpose
    TYPE==3 Reserved
    """
    CONTAINER_TYPE_MIXED:int=0
    CONTAINER_TYPE_VALUES:int=1
    CONTAINER_TYPE_MONO:int=2
    CONTAINER_TYPE_RESERVED:int=3

    @classmethod
    def createContainerInstance(cls,container_type:int,update_pallet_table:int):
        assert 0<=container_type<cls.CONTAINER_TYPE_RESERVED
        assert 0<=update_pallet_table<=0x0f
        return CellHeader((container_type<<4)|update_pallet_table)
    
    @classmethod
    def _vset2pallet(self,vset:Sequence[int])->int:
        if vset is None:
            return CellHeader.PALLET_NBIT
        bw=toBitWidth(len(vset))
        if bw<=1:
            return CellHeader.PALLET_1BIT
        elif bw<=2:
            return CellHeader.PALLET_2BIT
        elif bw<=4:
            return CellHeader.PALLET_4BIT
        return CellHeader.PALLET_NBIT

    @classmethod
    def createRawInstance(cls,vset:Sequence[int],update_pallet_table_low4:int=0):
        """ pallet_bitsはPALLET_?BITを指定
        """
        assert 0<=update_pallet_table_low4<=0x0f
        pallet_bits=cls._vset2pallet(vset)
        b=(1<<6)|(pallet_bits<<4)|update_pallet_table_low4
        return CellHeader(b)
    PALLET_1BIT:int=0
    PALLET_2BIT:int=1
    PALLET_4BIT:int=2
    PALLET_NBIT:int=3       #4ビット以上は実質マルチビットのパレット無しになった
    RLE_PALLET_2:int=0
    RLE_PALLET_3:int=1
    RLE_PALLET_5:int=2
    RLE_PALLET_16:int=3
    RLE_DATA_ENCODING_MBUINT:int=0
    RLE_DATA_ENCODING_SHORT_VALUE:int=1
    RLE_DATA_ENCODING_SINGLE_EDGE_ROW:int=2
    RLE_DATA_ENCODING_RESERVED:int=3
    RLE_MODE_Zigzag:int     =0
    RLE_MODE_Zigzag_MH:int  =1
    RLE_MODE_Zigzag_T:int   =2
    RLE_MODE_Zigzag_T_MV:int=3 #これ以上あってもほとんど変わらない悲しい事実
    # RLE_MODE_Digdag:int     =4
    # RLE_MODE_Digdag_MH:int  =5
    # RLE_MODE_Digdag_T:int   =6
    # RLE_MODE_Digdag_T_MV:int=7
    # RLE_MODE_Spiral:int=8
    # RLE_MODE_Normal:int=14
    # RLE_MODE_Normal_T:int=15
    @classmethod
    def createRleInstance(cls,vset:Sequence[int],scanMode:int,dataEncoding:int=RLE_DATA_ENCODING_MBUINT):
        assert vset is not None
        assert 1<=len(vset)<=16
        assert 0<=scanMode<=3
        assert dataEncoding in (
            cls.RLE_DATA_ENCODING_MBUINT,
            cls.RLE_DATA_ENCODING_SHORT_VALUE,
            cls.RLE_DATA_ENCODING_SINGLE_EDGE_ROW)
        if len(vset)<=2:
            pallet_mode=cls.RLE_PALLET_2
        elif len(vset)==3:
            pallet_mode=cls.RLE_PALLET_3
        elif len(vset)<=5:
            pallet_mode=cls.RLE_PALLET_5
        else:
            pallet_mode=cls.RLE_PALLET_16
        b=(2<<6)|(pallet_mode<<4)|(dataEncoding<<2)|scanMode
        return CellHeader(b)


    def __init__(self,byte1:int):
        self.byte1=byte1
    def __str__(self):
        s=""
        if self.isNode:
            return f"Node,containerType:{self.containerType},updatePalletTable4:{self.updatePalletTable4}"
        elif self.isRaw:
            return f"Raw,numPallet:{self.numOfPallet}"
        elif self.isRle:
            return f"Rle,numPallet:{self.numOfPallet},encoding:{self.rleDataEncoding},map:{self.rleMode}"
        raise RuntimeError()


    @property
    def isNode(self)->bool:
        return (self.byte1>>6)&0x3==0
    @property
    def isRaw(self)->bool:
        return (self.byte1>>6)&0x3==1
    @property
    def isRle(self)->bool:
        return (self.byte1>>6)&0x3==2
    @property
    def numOfPallet(self)->int:
        if self.isNode:
            return self.updatePalletTable4.bit_count()
        pr=self.palletResolution
        if self.isRle:
            return [2,3,5,16][pr]
        if pr==self.PALLET_NBIT:
            return None
        return [2,4,16][pr]
    @property
    def palletResolution(self)->int:
        """ PALLET_nBITを返す。
        """
        assert(self.isRaw or self.isRle)
        return (self.byte1>>4)&0x3

    @property
    def rawUpdatePalletTableLow4(self)->int:
        assert self.isRaw
        return self.byte1&0x0f

    @property
    def hasValidRawReservedBits(self)->bool:
        assert self.isRaw
        if self.palletResolution==self.PALLET_NBIT:
            return self.rawUpdatePalletTableLow4==0
        if self.palletResolution==self.PALLET_1BIT:
            return self.rawUpdatePalletTableLow4<0x04
        return True
    @property
    def rleMode(self)->int:
        assert(self.isRle)
        return self.byte1&0x03

    @property
    def rleDataEncoding(self)->int:
        assert(self.isRle)
        return (self.byte1>>2)&0x03

    @property
    def hasValidRleReservedBits(self)->bool:
        assert(self.isRle)
        return self.rleDataEncoding in (
            self.RLE_DATA_ENCODING_MBUINT,
            self.RLE_DATA_ENCODING_SHORT_VALUE,
            self.RLE_DATA_ENCODING_SINGLE_EDGE_ROW)

    @property
    def containerType(self)->int:
        assert self.isNode
        return (self.byte1>>4)&0x03

    @property
    def updatePalletTable4(self)->int:
        assert self.isNode
        return self.byte1&0x0f

    @property
    def hasValidContainerHeader(self)->bool:
        assert self.isNode
        update_table=self.updatePalletTable4
        return (
            self.containerType!=self.CONTAINER_TYPE_RESERVED
            and (
                self.containerType!=self.CONTAINER_TYPE_MIXED
                or update_table&0x01==0
            )
            and (
                self.containerType!=self.CONTAINER_TYPE_MONO
                or update_table&0x07==0
            )
        )
    
