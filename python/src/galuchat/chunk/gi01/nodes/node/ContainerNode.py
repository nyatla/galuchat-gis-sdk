from typing import List, Sequence

from galuchat.math import isPowOf2
from galuchat.math.raster import IReadableRaster, IWritableRaster
from .BaseNode import BaseNode
from .RawNode import RawNode


class ContainerNode(BaseNode):
    """ 2x2グリッドの値と値パターンをツリー構造で保持するクラス。
    包括Cell.N個のMonoValue、4-N個のSquareCellsNNを持つ
    グリッド親子構造を持ち、1/2（面積比1/4）の子値を4個内包する。ツリーの末端の解像度は2。
    子値が単一値である場合、子のに0以外を設定する。
    """
    _children:Sequence[BaseNode|int]
    def __init__(self,resolution:int,children:Sequence[BaseNode|int]):
        assert(len(children)==4)
        super().__init__(resolution)
        self._children=children
    @property
    def children(self)->Sequence[BaseNode|int]:
        return self._children
    @property
    def numOfMonoGrid(self)->int:
        """ 単色グリッドの数
        """
        return 4-([i if isinstance(i,int) else None for i in self.children].count(None))
    def toRaster(self,dest:IWritableRaster,x:int=0,y:int=0):
        wh2=self.resolution//2
        for i,c in enumerate(self.children):
            cx=x+(i%2)*wh2
            cy=y+(i//2)*wh2
            if isinstance(c,int):
                for iy in range(wh2):
                    for ix in range(wh2):
                        dest.set(cx+ix,cy+iy,c)
            elif isinstance(c,BaseNode):
                c.toRaster(dest,cx,cy)
            else:
                raise RuntimeError()

    @classmethod
    def parseRaster(cls,src:IReadableRaster,minsize:int):
        assert(isPowOf2(src.width))
        assert(src.width==src.height and src.width>=minsize*2)
        wh=src.width
        #四分木
        wh2=wh//2
        sub:List[IReadableRaster|int]=[
            src.createSubRaster(0,0,wh2,wh2),
            src.createSubRaster(wh2,0,wh2,wh2),
            src.createSubRaster(0,wh2,wh2,wh2),
            src.createSubRaster(wh2,wh2,wh2,wh2)
        ]
        node:Sequence[BaseNode|int]=list()
        for i in sub:
            vs=sorted(list(i.valueSet()))
            if len(vs)==1:
                node.append(vs[0])
            elif wh2>minsize:
                #コンテナに変換
                node.append(ContainerNode.parseRaster(i,minsize))
            else:
                #末端は非圧縮ノード
                node.append(RawNode.parseRaster(i))
        return ContainerNode(wh,node)

