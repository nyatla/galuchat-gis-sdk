from galuchat.io.BytesWriter import BytesWriter
from galuchat.io import ABytesReader
from galuchat.chunk.gi01.CellHeader import CellHeader
from galuchat.chunk.gi01.PalletHeader import PalletHeader
from .node import BaseNode,BaseDataNode
from .node import RawNode,RawPalletNode
from .node import RlePallet2Node,RlePallet3Node,RlePallet5Node,RlePallet16Node
from .node import ContainerNode
from galuchat.chunk.gi01.PalletMgr import PalletMgr
from .NodePallet import NodePallet
class NodeSerializer:
    """パレット更新値を絶対値(MBUInt)で書くGI01ノードシリアライザ。"""

    def _writePalletValues(self,dest:BytesWriter,updates):
        dest.writeMbUInts(updates)

    def _updatePallet(self,pallet,pmgr:PalletMgr):
        # prefix更新形式。最後に変化したスロットまでを先頭から書く。
        update_count=0
        for index,value in enumerate(pallet):
            if pmgr.table[index]!=value:
                update_count=index+1
        updates=pallet[:update_count]
        pmgr.put(updates)
        return updates

    def _updatePalletTable(self,pallet,pmgr:PalletMgr,width:int):
        # table更新形式。変化したスロットだけを更新フラグで示して書く。
        assert len(pallet)<=width
        update_table=0
        updates=[]
        for slot,value in enumerate(pallet):
            if pmgr.table[slot]==value:
                continue
            update_table|=1<<(width-1-slot)
            updates.append(value)
        pmgr.putByTable(update_table,updates,width)
        return update_table,updates

    def _serializeContainer(self,dest:BytesWriter,node:ContainerNode,pmgr:PalletMgr):
        values4=[child if isinstance(child,int) else None for child in node.children]
        values=sorted({value for value in values4 if value is not None})
        if node.numOfMonoGrid==4 and len(values)==1:
            update_table,updates=self._updatePalletTable(values,pmgr,4)
            dest.writeByte(CellHeader.createContainerInstance(
                CellHeader.CONTAINER_TYPE_MONO,update_table).byte1)
            self._writePalletValues(dest,updates)
            return

        container_type=(
            CellHeader.CONTAINER_TYPE_VALUES
            if node.numOfMonoGrid==4
            else CellHeader.CONTAINER_TYPE_MIXED)
        node_pallet,pallet=NodePallet.create(values4,container_type)
        update_table,updates=self._updatePalletTable(pallet,pmgr,4)
        dest.writeByte(CellHeader.createContainerInstance(
            container_type,update_table).byte1)
        dest.writeByte(node_pallet.mask)
        self._writePalletValues(dest,updates)

        if container_type==CellHeader.CONTAINER_TYPE_VALUES:
            return
        for child in node.children:
            if isinstance(child,int):
                continue
            if isinstance(child,ContainerNode):
                self._serializeContainer(dest,child,pmgr)
            elif isinstance(child,BaseDataNode):
                self._serializeNode(dest,child,pmgr)
            else:
                raise RuntimeError()
    def _serializeNode(self,dest:BytesWriter,node:BaseDataNode,pmgr:PalletMgr):
        if isinstance(node,RawNode):
            dest.writeByte(CellHeader.createRawInstance(None).byte1)
            dest.writeBytes(node.getBytes())
        elif isinstance(node,RawPalletNode):
            pallet_resolution=CellHeader.createRawInstance(node.pallet).palletResolution
            update_width=[2,4,16][pallet_resolution]
            update_control,updates=self._updatePalletTable(
                node.pallet,pmgr,update_width)
            update_low4=update_control&0x0f
            header=CellHeader.createRawInstance(node.pallet,update_low4)
            dest.writeByte(header.byte1)
            if header.palletResolution==CellHeader.PALLET_4BIT:
                dest.writeBitsFromInt32(update_control>>4,12)
            if len(updates)>0:
                self._writePalletValues(dest,updates)
            nbits=ABytesReader.toBitWidth(len(node.pallet))
            dest.writeBitBytes(node.getBytes(),node.resolution**2*nbits)
        elif isinstance(node,(RlePallet2Node,RlePallet3Node,RlePallet5Node,RlePallet16Node)):
            header=CellHeader.createRleInstance(
                node.pallet,node.mode,node.dataEncoding)
            update_width=[2,3,5,16][header.palletResolution]
            update_control,updates=self._updatePalletTable(
                node.pallet,pmgr,update_width)
            value_bits_add=(
                node.valueBitsAdd
                if node.dataEncoding in (
                    CellHeader.RLE_DATA_ENCODING_SHORT_VALUE,
                    CellHeader.RLE_DATA_ENCODING_SINGLE_EDGE_ROW)
                else 0)
            pallet_header=PalletHeader.create(
                header.palletResolution,update_control,node.initialIndex,value_bits_add)
            dest.writeByte(header.byte1)
            pallet_header.writeTo(dest)
            # 更新対象がある場合だけパレット値列を書く。
            if len(updates)>0:
                self._writePalletValues(dest,updates)
            dest.writeBitBytes(node.getBytes(),node.dataBitCount)
        else:
            raise RuntimeError()

    def serialize(self,dest:BytesWriter,node:BaseNode,pmgr:PalletMgr=None):
        if pmgr is None:
            pmgr=PalletMgr(16)
        if isinstance(node,ContainerNode):
            self._serializeContainer(dest,node,pmgr)
        elif isinstance(node,BaseNode):
            self._serializeNode(dest,node,pmgr)
        else:
            raise RuntimeError()   


class DeltaNodeSerializer(NodeSerializer):
    """パレット更新値を直前値との差分(MBInt)で書くGI01ノードシリアライザ。"""

    def _writePalletValues(self,dest:BytesWriter,updates):
        for delta in updates:
            dest.writeMbInt(delta)

    def _updatePallet(self,pallet,pmgr:PalletMgr):
        # prefix更新形式では、更新対象スロットごとに現在値との差分を書き出す。
        update_count=0
        for index,value in enumerate(pallet):
            if pmgr.table[index]!=value:
                update_count=index+1
        updates=[
            value-pmgr.table[index]
            for index,value in enumerate(pallet[:update_count])
        ]
        pmgr.put(pallet[:update_count])
        return updates

    def _updatePalletTable(self,pallet,pmgr:PalletMgr,width:int):
        # table更新形式でも、更新フラグの立ったスロットだけ差分値を並べる。
        assert len(pallet)<=width
        update_table=0
        updates=[]
        values=[]
        for slot,value in enumerate(pallet):
            if pmgr.table[slot]==value:
                continue
            update_table|=1<<(width-1-slot)
            updates.append(value-pmgr.table[slot])
            values.append(value)
        pmgr.putByTable(update_table,values,width)
        return update_table,updates
