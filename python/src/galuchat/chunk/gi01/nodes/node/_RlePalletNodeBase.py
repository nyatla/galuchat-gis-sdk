from typing import Iterator,Sequence

from galuchat.io import ABytesReader,ABytesWriter,BytesBufferReader,BytesWriter
from galuchat.io.MBIntDef import MBIntDef
from galuchat.chunk.gi01.CellHeader import CellHeader
from galuchat.chunk.gi01.RlePacketReader import RlePacketReader
from galuchat.chunk.gi01.rlelencodec import ShortValueRleLenCodec, SingleEdgeRowLenCodec
from galuchat.math.raster import IReadableRaster,IWritableRaster
from .BaseNode import BaseDataNode,BasePalletDataNode
from .IndexMapset import IndexMapset
from ._rlecp import rlecp


class RlePalletNodeBase(BasePalletDataNode):
    PALLET_MODE:int
    MIN_PALLET_SIZE:int
    MAX_PALLET_SIZE:int

    def __init__(
        self,
        resolution:int,
        data:bytes,
        pallet:Sequence[int],
        mode:int,
        initial_index:int|None,
        data_encoding:int=CellHeader.RLE_DATA_ENCODING_MBUINT,
        value_bits_add:int=0,
        data_bit_count:int|None=None):
        assert self.MIN_PALLET_SIZE<=len(pallet)<=self.MAX_PALLET_SIZE
        assert data_encoding in (
            CellHeader.RLE_DATA_ENCODING_MBUINT,
            CellHeader.RLE_DATA_ENCODING_SHORT_VALUE,
            CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW)
        assert 0<=value_bits_add<=15
        if data_encoding==CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW:
            assert self._hasValidSingleEdgeParams(value_bits_add)
        elif data_encoding==CellHeader.RLE_DATA_ENCODING_SHORT_VALUE:
            assert value_bits_add<=7
        else:
            assert value_bits_add==0
        super().__init__(resolution,pallet)
        self._data=data
        self._data_bit_count=len(data)*8 if data_bit_count is None else data_bit_count
        self._mode=mode
        self._initial_index=initial_index
        self._data_encoding=data_encoding
        self._value_bits_add=value_bits_add

    @classmethod
    def parseRaster(cls,src:IReadableRaster,pallet:Sequence[int])->BaseDataNode:
        assert src.width*src.height%8==0 and src.width==src.height
        assert cls.MIN_PALLET_SIZE<=len(pallet)<=cls.MAX_PALLET_SIZE
        scan_mode,packet,initial_index,data_encoding,value_bits_add,bit_count=cls._encodePacket(
            src.toArray(),src.width,pallet)
        return cls(src.width,packet,pallet,scan_mode,initial_index,data_encoding,value_bits_add,bit_count)

    @classmethod
    def _shortValueBitsAdd(cls,value_bits_add:int)->int:
        return RlePacketReader._shortValueBitsAdd(value_bits_add)

    @classmethod
    def _shortValueRunBitsAdd(cls,value_bits_add:int)->int:
        return RlePacketReader._shortValueRunBitsAdd(value_bits_add)

    @classmethod
    def _singleEdgeDValueFormat(cls,value_bits_add:int)->int:
        return RlePacketReader._singleEdgeDValueFormat(value_bits_add)

    @classmethod
    def _singleEdgeMbUIntReduceBits(cls,value_bits_add:int)->int|None:
        return RlePacketReader._singleEdgeMbUIntReduceBits(value_bits_add)

    @classmethod
    def _singleEdgeReduceBitCandidates(cls)->tuple[int,...]:
        return (2,3,4,5)

    @classmethod
    def _packSingleEdgeParams(cls,d_value_format:int,mbuint_reduce_bits:int|None)->int:
        reduce_code=0 if mbuint_reduce_bits is None else mbuint_reduce_bits-1
        if not 0<=d_value_format<=2 or not 0<=reduce_code<=4:
            raise ValueError("invalid SingleEdge EncodingParams")
        return d_value_format*5+reduce_code

    @classmethod
    def _hasValidSingleEdgeParams(cls,value_bits_add:int)->bool:
        return 0<=value_bits_add<=14

    @classmethod
    def _countBits(
        cls,
        counts:Sequence[int],
        resolution:int,
        data_encoding:int,
        value_bits_add:int=0)->int:
        if data_encoding==CellHeader.RLE_DATA_ENCODING_MBUINT:
            writer=BytesWriter()
            return writer.writeMbUInts(counts)*8
        if data_encoding==CellHeader.RLE_DATA_ENCODING_SHORT_VALUE:
            return ShortValueRleLenCodec(
                resolution,
                cls._shortValueBitsAdd(value_bits_add),
                cls._shortValueRunBitsAdd(value_bits_add)).estimateBits(counts)
        if data_encoding==CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW:
            return SingleEdgeRowLenCodec(
                resolution,
                cls._singleEdgeDValueFormat(value_bits_add),
                cls._singleEdgeMbUIntReduceBits(value_bits_add)).estimateBits(counts)
        raise ValueError("invalid RLE data encoding")

    @classmethod
    def _selectCountEncoding(
        cls,
        counts:Sequence[int],
        resolution:int,
        data_encoding:int,
        value_bits_add:int=0)->tuple[int,int]:
        if data_encoding!=CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW:
            return cls._countBits(counts,resolution,data_encoding,value_bits_add),value_bits_add
        codec=SingleEdgeRowLenCodec(
            resolution,
            cls._singleEdgeDValueFormat(value_bits_add),
            None)
        bit_count,mbuint_reduce_bits=codec.selectEncoding(
            counts,cls._singleEdgeReduceBitCandidates())
        selected_value_bits_add=cls._packSingleEdgeParams(
            cls._singleEdgeDValueFormat(value_bits_add),
            mbuint_reduce_bits)
        return bit_count,selected_value_bits_add

    @classmethod
    def _indexBits(cls,count_count:int)->int:
        if cls.PALLET_MODE==1:
            return max(0,count_count-1)
        if cls.PALLET_MODE==2:
            return max(0,count_count-1)*2
        if cls.PALLET_MODE==3:
            return count_count*4
        return 0

    @classmethod
    def _writeIndexAt(cls,dest:ABytesWriter,indices:Sequence[int],run_index:int)->int:
        if cls.PALLET_MODE==0:
            return 0
        if cls.PALLET_MODE==1:
            if run_index==0:
                return 0
            dest.writeBitsFromInt32((indices[run_index]-indices[run_index-1]-1)%3,1)
            return 1
        if cls.PALLET_MODE==2:
            if run_index==0:
                return 0
            dest.writeBitsFromInt32((indices[run_index]-indices[run_index-1]-1)%5,2)
            return 2
        if cls.PALLET_MODE==3:
            dest.writeBitsFromInt32(indices[run_index],4)
            return 4
        raise ValueError("invalid RLE pallet mode")

    @classmethod
    def _writeIndicesForRuns(
        cls,
        dest:ABytesWriter,
        indices:Sequence[int],
        start:int,
        count:int)->int:
        bit_count=0
        for run_index in range(start,start+count):
            bit_count+=cls._writeIndexAt(dest,indices,run_index)
        return bit_count

    @classmethod
    def _readNextIndex(
        cls,
        src:ABytesReader,
        initial_index:int|None,
        run_index:int,
        previous_index:int|None)->int:
        return RlePacketReader.readNextIndex(
            src,cls.PALLET_MODE,initial_index,run_index,previous_index)

    @classmethod
    def writePacket(
        cls,
        dest:ABytesWriter,
        counts:Sequence[int],
        indices:Sequence[int],
        resolution:int,
        data_encoding:int=CellHeader.RLE_DATA_ENCODING_MBUINT,
        value_bits_add:int=0,
        align_counts:bool=True,
        align_indices:bool=True)->int:
        if len(counts)!=len(indices):
            raise ValueError("RLE counts and indices length mismatch")
        align=align_counts or align_indices
        bit_count=0
        if data_encoding==CellHeader.RLE_DATA_ENCODING_MBUINT:
            for run_index,count in enumerate(counts):
                dest.writeMbUInt(count)
                bit_count+=MBIntDef.sizeOfMbUint(count)*8
                bit_count+=cls._writeIndexAt(dest,indices,run_index)
        elif data_encoding==CellHeader.RLE_DATA_ENCODING_SHORT_VALUE:
            codec=ShortValueRleLenCodec(
                resolution,
                cls._shortValueBitsAdd(value_bits_add),
                cls._shortValueRunBitsAdd(value_bits_add))
            bit_count+=codec.writeRunCount(dest,counts)
            run_index=0
            for token in codec.selectTokens(counts):
                token_count=token.next_index-run_index
                bit_count+=codec.writeToken(dest,token)
                bit_count+=cls._writeIndicesForRuns(dest,indices,run_index,token_count)
                run_index=token.next_index
            if run_index!=len(counts)-1:
                raise RuntimeError("RLE short value token plan does not cover explicit runs")
            bit_count+=cls._writeIndexAt(dest,indices,len(counts)-1)
        elif data_encoding==CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW:
            codec=SingleEdgeRowLenCodec(
                resolution,
                cls._singleEdgeDValueFormat(value_bits_add),
                cls._singleEdgeMbUIntReduceBits(value_bits_add))
            plan=codec.selectPlan(counts)
            bit_count+=codec.writeRunCount(dest,counts)
            if plan.mbuint_reduce_bits is None:
                run_index=0
                for token in plan.tokens:
                    token_count=token.next_index-run_index
                    bit_count+=codec.writeToken(dest,token)
                    bit_count+=cls._writeIndicesForRuns(dest,indices,run_index,token_count)
                    run_index=token.next_index
                if run_index!=len(counts)-1:
                    raise RuntimeError("RLE single edge token plan does not cover explicit runs")
            else:
                bit_count+=codec.writeReduceFirstValue(dest,counts)
                bit_count+=cls._writeIndexAt(dest,indices,0)
                middle_index=0
                for token in plan.tokens:
                    token_count=token.next_index-middle_index
                    run_index=middle_index+1
                    bit_count+=codec.writeToken(dest,token)
                    bit_count+=cls._writeIndicesForRuns(dest,indices,run_index,token_count)
                    middle_index=token.next_index
                if middle_index!=len(counts)-2:
                    raise RuntimeError("RLE single edge reduce token plan does not cover middle runs")
            bit_count+=cls._writeIndexAt(dest,indices,len(counts)-1)
        else:
            raise ValueError("invalid RLE data encoding")
        if align:
            dest.alignToByte()
        return bit_count

    @classmethod
    def _encodePacket(cls,data:Sequence[int],resolution:int,pallet:Sequence[int])->tuple[int,bytes,int|None,int,int,int]:
        candidates:list[tuple[int,bytes,int|None,int,int,int]]=[]
        value_to_index={value:index for index,value in enumerate(pallet)}
        for scan_mode,index_map in IndexMapset.getIndexMaps(resolution):
            counts,values=rlecp(index_map.wrapIterator(iter(data),True))
            indices=[value_to_index[value] for value in values]
            initial_index=None
            if cls.PALLET_MODE in (0,1,2):
                initial_index=indices[0]
            elif cls.PALLET_MODE!=3:
                raise ValueError("invalid RLE pallet mode")
            for data_encoding in (
                CellHeader.RLE_DATA_ENCODING_MBUINT,
                CellHeader.RLE_DATA_ENCODING_SHORT_VALUE,
                CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW,
            ):
                if data_encoding==CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW and len(counts)<2:
                    # SingleEdgeRowは最終ランを省略する形式なので、単一ランは候補にしない。
                    continue
                if data_encoding==CellHeader.RLE_DATA_ENCODING_SHORT_VALUE:
                    value_bits_adds=range(8)
                elif data_encoding==CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW:
                    value_bits_adds=tuple(
                        cls._packSingleEdgeParams(d_value_format,None)
                        for d_value_format in (0,1,2))
                else:
                    value_bits_adds=(0,)
                for value_bits_add in value_bits_adds:
                    _,selected_value_bits_add=cls._selectCountEncoding(
                        counts,resolution,data_encoding,value_bits_add)
                    writer=BytesWriter()
                    bit_count=cls.writePacket(
                        writer,counts,indices,resolution,data_encoding,selected_value_bits_add,True,True)
                    packet=bytes(writer.buffer)
                    candidates.append((
                        scan_mode,packet,initial_index,data_encoding,selected_value_bits_add,bit_count))
        selected=min(candidates,key=lambda candidate:candidate[5])
        return selected[:6]

    @classmethod
    def decodePacket(
        cls,
        data:bytes,
        resolution:int,
        initial_index:int|None,
        data_encoding:int=CellHeader.RLE_DATA_ENCODING_MBUINT,
        value_bits_add:int=0)->tuple[list[int],list[int]]:
        return cls._decodePacketFromReader(
            BytesBufferReader(data),resolution,initial_index,data_encoding,value_bits_add)

    @classmethod
    def _decodePacketFromReader(
        cls,
        reader:ABytesReader,
        resolution:int,
        initial_index:int|None,
        data_encoding:int,
        value_bits_add:int)->tuple[list[int],list[int]]:
        counts:list[int]=[]
        indices:list[int]=[]
        for count,pallet_index in cls.iterRunsFromReader(
            reader,resolution,initial_index,data_encoding,value_bits_add):
            counts.append(count)
            indices.append(pallet_index)
        return counts,indices

    @classmethod
    def iterRunsFromReader(
        cls,
        reader:ABytesReader,
        resolution:int,
        initial_index:int|None,
        data_encoding:int=CellHeader.RLE_DATA_ENCODING_MBUINT,
        value_bits_add:int=0)->Iterator[tuple[int,int]]:
        yield from RlePacketReader.iterRunsFromReader(
            reader,
            resolution,
            cls.PALLET_MODE,
            initial_index,
            data_encoding,
            value_bits_add)

    @classmethod
    def decodePacketFromReader(
        cls,
        reader:ABytesReader,
        resolution:int,
        initial_index:int|None,
        data_encoding:int=CellHeader.RLE_DATA_ENCODING_MBUINT,
        value_bits_add:int=0)->tuple[list[int],list[int]]:
        return cls._decodePacketFromReader(
            reader,resolution,initial_index,data_encoding,value_bits_add)

    @classmethod
    def readPacketWithBitCount(
        cls,
        src:ABytesReader,
        resolution:int,
        initial_index:int|None,
        data_encoding:int=CellHeader.RLE_DATA_ENCODING_MBUINT,
        value_bits_add:int=0)->tuple[bytes,list[int],int]:
        counts,indices=cls._decodePacketFromReader(
            src,resolution,initial_index,data_encoding,value_bits_add)
        writer=BytesWriter()
        bit_count=cls.writePacket(
            writer,counts,indices,resolution,data_encoding,value_bits_add,True,True)
        packet=bytes(writer.buffer)
        return packet,indices,bit_count

    @classmethod
    def readPacket(
        cls,
        src:ABytesReader,
        resolution:int,
        initial_index:int|None,
        data_encoding:int=CellHeader.RLE_DATA_ENCODING_MBUINT,
        value_bits_add:int=0)->tuple[bytes,list[int]]:
        packet,indices,_=cls.readPacketWithBitCount(
            src,resolution,initial_index,data_encoding,value_bits_add)
        return packet,indices

    @property
    def mode(self)->int:
        return self._mode

    @property
    def initialIndex(self)->int|None:
        return self._initial_index

    @property
    def dataEncoding(self)->int:
        return self._data_encoding

    @property
    def valueBitsAdd(self)->int:
        return self._value_bits_add

    def getBytes(self)->bytes:
        return self._data

    @property
    def dataBitCount(self)->int:
        return self._data_bit_count

    def toRaster(self,dest:IWritableRaster,x:int=0,y:int=0):
        counts,indices=self.decodePacket(
            self._data,self.resolution,self.initialIndex,self.dataEncoding,self.valueBitsAdd)
        index_map=IndexMapset.getIndexMap(self.resolution,self.mode)
        position=0
        for count,pallet_index in zip(counts,indices):
            value=self.pallet[pallet_index]
            for _ in range(count):
                mapped=index_map.map(position)
                dest.set(x+mapped%self.resolution,y+mapped//self.resolution,value)
                position+=1
