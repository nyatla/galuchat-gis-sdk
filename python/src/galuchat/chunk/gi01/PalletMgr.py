from typing import Union,Dict,List,Tuple,Iterable,Iterator,Sequence

class PalletMgr:
    """ カスケードパレット用のテーブル
    """
    def __init__(self,length:int=0):
        self._d=[0]*length
    def put(self,v:Sequence[int])->False:
        """ dの先頭からlen(v)個を置き換える。
            更新が行われるとTrue
        """
        lv=len(v)
        if lv==0:
            return False    #パレットが空の場合
        if self._d[0:lv]==v:
            return False    #パレットの先頭と完全に一致する場合
        #パレットの上書き
        for i in range(lv):
            self._d[i]=v[i]
        return True
    def putByTable(self,update_table:int,values:Sequence[int],width:int)->bool:
        """ update_tableで指定された位置だけを置き換える。
        """
        assert 0<=width<=len(self._d)
        assert 0<=update_table<(1<<width)
        if len(values)!=update_table.bit_count():
            raise ValueError("update value count does not match update table")
        is_updated=False
        value_index=0
        for slot in range(width):
            bit=1<<(width-1-slot)
            if update_table&bit==0:
                continue
            value=values[value_index]
            value_index+=1
            if self._d[slot]!=value:
                self._d[slot]=value
                is_updated=True
        return is_updated
    def get(self,size:int,start:int=0)->List[int]:
        """ dの先頭からsize個の値を返す。
        """
        return self._d[start:start+size]
    @property
    def table(self)->List[int]:
        """ テーブル全体を返す
        """
        return self._d
