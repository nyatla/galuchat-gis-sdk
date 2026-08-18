from typing import Sequence

from galuchat.chunk.gi01.PalletMgr import PalletMgr
from galuchat.chunk.gi01.CellHeader import CellHeader
from galuchat.chunk.gi01.PalletHeader import PalletHeader
from galuchat.io import ABytesReader, BytesWriter
from .NodePallet import NodePallet
from .node import (
    BaseDataNode,
    BaseNode,
    ContainerNode,
    RawNode,
    RawPalletNode,
    RlePallet16Node,
    RlePallet2Node,
    RlePallet3Node,
    RlePallet5Node,
)


class NodeDeserializer:
    """NodeSerializerの絶対値(MBUInt)形式を、対応するNodeクラスへ復元する。"""

    @staticmethod
    def _tableSlots(update_table:int,width:int)->list[int]:
        return [
            slot
            for slot in range(width)
            if update_table&(1<<(width-1-slot))
        ]

    def _readPalletValuesBySlots(self,src:ABytesReader,pmgr:PalletMgr,slots:list[int])->list[int]:
        return src.readMbUInts(len(slots))

    def _readPalletValuesPrefix(self,src:ABytesReader,pmgr:PalletMgr,count:int)->list[int]:
        return self._readPalletValuesBySlots(src,pmgr,list(range(count)))

    def _readDataPallet(self,header:CellHeader,src:ABytesReader,pmgr:PalletMgr)->Sequence[int]:
        update_low4=header.rawUpdatePalletTableLow4
        if header.palletResolution==CellHeader.PALLET_4BIT:
            update_control=(src.readBitsAsInt32(12)<<4)|update_low4
            slots=self._tableSlots(update_control,16)
            if len(slots)>0:
                pmgr.putByTable(
                    update_control,
                    self._readPalletValuesBySlots(src,pmgr,slots),
                    16)
            return pmgr.get(header.numOfPallet)
        update_width=[2,4][header.palletResolution]
        update_control=update_low4
        if update_control>=(1<<update_width):
            raise ValueError("RAW/P pallet update table has reserved bits")
        if update_control>0:
            slots=self._tableSlots(update_control,update_width)
            pmgr.putByTable(
                update_control,
                self._readPalletValuesBySlots(src,pmgr,slots),
                update_width)
        return pmgr.get(header.numOfPallet)

    def _deserializeDataNode(self,resolution:int,header:CellHeader,src:ABytesReader,pmgr:PalletMgr)->BaseDataNode:
        if header.isRaw:
            if not header.hasValidRawReservedBits:
                raise ValueError("RAW CellHeader reserved bits are not zero")
            if header.palletResolution==CellHeader.PALLET_NBIT:
                bw=BytesWriter()
                bw.writeMbUInts(src.readMbUInts(resolution**2))
                return RawNode(resolution,bytes(bw.buffer))
            pallet=self._readDataPallet(header,src,pmgr)
            if header.palletResolution==CellHeader.PALLET_1BIT:
                nbits=1
            elif header.palletResolution==CellHeader.PALLET_2BIT:
                nbits=2
            elif header.palletResolution==CellHeader.PALLET_4BIT:
                nbits=4
            else:
                raise RuntimeError()
            data=src.readAsBitBytes(resolution**2*nbits)
            return RawPalletNode(resolution,data,pallet)

        if header.isRle:
            if not header.hasValidRleReservedBits:
                raise ValueError("RLE CellHeader data encoding is reserved")
            pallet_header=PalletHeader.readFrom(src,header.palletResolution)
            value_bits_add=(
                pallet_header.valueBitsAdd
                if header.rleDataEncoding in (
                    CellHeader.RLE_DATA_ENCODING_SHORT_VALUE,
                    CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW)
                else 0)
            if (
                header.rleDataEncoding==CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW and
                pallet_header.valueBitsAdd>14
            ):
                raise ValueError("RLE SingleEdgeRow EncodingParams is reserved")
            if (
                header.rleDataEncoding==CellHeader.RLE_DATA_ENCODING_SHORT_VALUE and
                pallet_header.valueBitsAdd>0x07
            ):
                raise ValueError("RLE ShortValue EncodingParams is reserved")
            if header.rleDataEncoding not in (
                CellHeader.RLE_DATA_ENCODING_SHORT_VALUE,
                CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW) and pallet_header.valueBitsAdd!=0:
                raise ValueError("RLE PalletHeader encoding params must be zero")
            if pallet_header.updatePalletTable is not None:
                update_table=pallet_header.updatePalletTable
                if update_table>0:
                    slots=self._tableSlots(update_table,pallet_header.capacity)
                    pmgr.putByTable(
                        update_table,
                        self._readPalletValuesBySlots(src,pmgr,slots),
                        pallet_header.capacity)
            elif pallet_header.updateCount>0:
                pmgr.put(self._readPalletValuesPrefix(src,pmgr,pallet_header.updateCount))
            node_types=(RlePallet2Node,RlePallet3Node,RlePallet5Node,RlePallet16Node)
            node_type=node_types[header.palletResolution]
            data,indices,data_bit_count=node_type.readPacketWithBitCount(
                src,resolution,pallet_header.initialIndex,header.rleDataEncoding,value_bits_add)
            pallet_count=max(indices)+1
            expected_ranges=((1,2),(3,3),(4,5),(6,16))
            minimum,maximum=expected_ranges[header.palletResolution]
            if not minimum<=pallet_count<=maximum:
                raise ValueError("RLE pallet index range does not match encoding mode")
            pallet=pmgr.get(pallet_count)
            return node_type(
                resolution,data,pallet,header.rleMode,
                pallet_header.initialIndex,header.rleDataEncoding,value_bits_add,data_bit_count)

        raise RuntimeError()

    def _deserializeContainer(self,resolution:int,header:CellHeader,src:ABytesReader,pmgr:PalletMgr)->ContainerNode:
        if not header.hasValidContainerHeader:
            raise ValueError("invalid ContainerNode CellHeader")
        container_type=header.containerType
        mask=(
            src.readByte()
            if container_type!=CellHeader.CONTAINER_TYPE_MONO
            else None)
        update_table=header.updatePalletTable4
        if update_table>0:
            slots=self._tableSlots(update_table,4)
            pmgr.putByTable(
                update_table,
                self._readPalletValuesBySlots(src,pmgr,slots),
                4)

        if container_type==CellHeader.CONTAINER_TYPE_MONO:
            return ContainerNode(resolution,[pmgr.get(1)[0]]*4)

        node_pallet=NodePallet.restore(
            mask,container_type,pmgr.get(4))
        children:list[BaseNode|int]=[]
        for index in range(4):
            value=node_pallet.palletValue(index)
            if value is not None:
                children.append(value)
                continue
            child_header=CellHeader(src.readByte())
            children.append(self._deserialize(resolution//2,child_header,src,pmgr))
        return ContainerNode(resolution,children)

    def _deserialize(self,resolution:int,header:CellHeader,src:ABytesReader,pmgr:PalletMgr)->BaseNode:
        if header.isNode:
            return self._deserializeContainer(resolution,header,src,pmgr)
        return self._deserializeDataNode(resolution,header,src,pmgr)

    def deserialize(self,resolution:int,src:ABytesReader,pmgr:PalletMgr|None=None)->BaseNode:
        if pmgr is None:
            pmgr=PalletMgr(16)
        return self._deserialize(resolution,CellHeader(src.readByte()),src,pmgr)


class DeltaNodeDeserializer(NodeDeserializer):
    """DeltaNodeSerializerの差分(MBInt)形式を、対応するNodeクラスへ復元する。"""

    def _readPalletValuesBySlots(self,src:ABytesReader,pmgr:PalletMgr,slots:list[int])->list[int]:
        return [
            pmgr.table[slot]+src.readMbInt()
            for slot in slots
        ]
