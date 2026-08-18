from typing import Tuple

from galuchat.math.indexmap import (
    ChaindIndexMap,
    IndexMap,
    MirrorIndexMap,
    TransposeIndexMap,
    ZigzagIndexMap,
)
from galuchat.chunk.gi01.CellHeader import CellHeader


class IndexMapset:
    @classmethod
    def getIndexMaps(cls,resolution:int)->Tuple[IndexMap]:
        return (
        (CellHeader.RLE_MODE_Zigzag,ZigzagIndexMap(resolution),),
        (CellHeader.RLE_MODE_Zigzag_MH,ChaindIndexMap([MirrorIndexMap(resolution,True,False),ZigzagIndexMap(resolution)]),),   #水平ミラー
        (CellHeader.RLE_MODE_Zigzag_T,ChaindIndexMap([ZigzagIndexMap(resolution),TransposeIndexMap(resolution)]),),           #Transpose
        (CellHeader.RLE_MODE_Zigzag_T_MV,ChaindIndexMap([MirrorIndexMap(resolution,False,True),ZigzagIndexMap(resolution),TransposeIndexMap(resolution)]),),   #転置水平ミラー
        )
    @classmethod
    def getIndexMap(cls,resolution:int,mode:int)->IndexMap:
        if mode==CellHeader.RLE_MODE_Zigzag:
            return ZigzagIndexMap(resolution)
        if mode==CellHeader.RLE_MODE_Zigzag_MH:
            return ChaindIndexMap([
                MirrorIndexMap(resolution,True,False),
                ZigzagIndexMap(resolution)])
        if mode==CellHeader.RLE_MODE_Zigzag_T:
            return ChaindIndexMap([
                ZigzagIndexMap(resolution),
                TransposeIndexMap(resolution)])
        if mode==CellHeader.RLE_MODE_Zigzag_T_MV:
            return ChaindIndexMap([
                MirrorIndexMap(resolution,False,True),
                ZigzagIndexMap(resolution),
                TransposeIndexMap(resolution)])
        raise RuntimeError()
