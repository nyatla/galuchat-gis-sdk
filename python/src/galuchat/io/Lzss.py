import os,sys
from typing import Iterator,Iterable,List,Union,Tuple

from .ABytesReader import ABytesReader
from .BytesIteratorReader import BytesIteratorReader
from .BytesWriter import BytesWriter

class Lzss:
    MAX_MATCH_SIZE=16
    class SlidingWindow:
        def __init__(self,size:int,padding:int=0):
            self._pdict=[padding]*size
            self._ptr=0 #現在のウインドウの先頭
        def __len__(self)->int:
            return len(self._pdict)
        def get(self,idx:int)->int:
            """ n番目の値を得る
            """
            l=len(self._pdict)
            return self._pdict[(self._ptr+idx)%l]
        def gets(self,idx:int,size:int)->List[int]:
            """ n番目の値を得る
            """
            b=self._pdict
            p=self._ptr
            l=len(b)
            return [b[(p+i+idx)%l] for i in range(size)]

        def push(self,v:int):
            """ スライディングウインドウに追記してポインタを進める。
            """
            l=len(self._pdict)
            self._pdict[self._ptr]=v
            self._ptr=(self._ptr+1)%l
        def pushs(self,v:List[int]):
            """ スライディングウインドウに追記してポインタを進める。
            """
            for i in v:
                self.push(i)

        def match(self,idx:int,v:List[int]):
            """ idxから始まる要素がvと一致するかを返す。
            """
            b=self._pdict
            bs=len(self._pdict)
            ll=len(v)
            p=self._ptr
            for i in range(ll):
                if b[(idx+i+p)%bs]!=v[i]:
                    return False
            return True

        def search(self,v:List[int])->int:
            c=len(self._pdict)-len(v)+1 #テストする値の長さを引いた回数チェック
            for i in range(c):
                if self.match(i,v):
                    return i
            return None
    class MBuffer:
        def __init__(self):
            self._buf=[]
        def pushRef(self,pos:int,size:int):
            b=self._buf
            b.append((1,pos,size))
        def pushValue(self,v:int):
            b=self._buf
            b.append((0,v))

        def pushValues(self,v:List[int]):
            b=self._buf
            b.append((0,v.copy()))


    def __init__(self,window_size:int=16):
        self._sw_size=window_size
    def compress(self,src:Union[Iterator[int],Iterable[int]])->Union[Tuple[int,List[int]],Tuple[int]]:
        sw=self.SlidingWindow(self._sw_size)
        # sw_len=len(sw)
        mbuf=self.MBuffer()

        tmp=[]
        found_sp=None
        found_len=None
        siter=src if isinstance(src,Iterator) else iter(src)

        tmp.append(next(siter))
        try:
            while True:
                tmp_len=len(tmp)
                sp=sw.search(tmp)
                if sp is not None:
                    #見つかってかつ最長の場合がない !!!
                    if tmp_len==self.MAX_MATCH_SIZE:
                        mbuf.pushRef(sp,tmp_len)
                        sw.pushs(tmp)
                        found_sp=None
                        tmp.clear()
                    else:
                        found_sp=sp
                        found_len=tmp_len
                    tmp.append(next(siter))# new
                    continue
                #一致する要素はない
                if found_sp is None:
                    #何も見つかっていない
                    assert(len(tmp)==1)
                    mbuf.pushValue(tmp[0]) #バッファにフラグ0とともに書込み
                    sw.pushs(tmp)
                    tmp.clear()
                    tmp.append(next(siter))# new
                    continue
                else:
                    #見つかったけど1文字
                    if tmp_len<=2:
                        mbuf.pushValue(tmp[0])
                        sw.push(tmp[0])
                        tmp=tmp[1:]
                    else:
                        mbuf.pushRef(found_sp,found_len)
                        sw.pushs(tmp[:found_len])
                        tmp=tmp[found_len:]
                    found_sp=None
        except StopIteration:
            pass
        if found_sp is None:
            pass
            # assert(len(tmp)==1)
            # mbuf.pushValue(tmp[0]) #バッファにフラグ0とともに書込み
        else:
            if tmp_len==1:
                mbuf.pushValue(tmp[0])
            else:
                mbuf.pushRef(found_sp,found_len)
        sw.pushs(tmp)
        return mbuf._buf
    def decompress(self,src:Iterator[Union[Tuple[int,List[int]],Tuple[int]]]):
        sw=self.SlidingWindow(self._sw_size)
        dest=bytearray()
        for d in src:
            if d[0]==0:
                dest.append(d[1])
                sw.push(d[1])
            elif d[0]==1:
                n=sw.gets(d[1],d[2])
                dest.extend(n)
                sw.pushs(n)
            else:
                raise RuntimeError()
        return dest
    def compressToBytes(self,src:Union[Iterator[int],Iterable[int]])->bytearray:
        """ バイトストリームとして圧縮する。slidingwindowは256未満であること。    
        size[MBInt],LZSS-stream[n],padding
        LZSS-stream[n]:
            値は 0:1に続けてn:3の個数を書き込む
            参照は 1:1に続けてn:8の位置とm:4の長さを書き込む
        """
        assert(self.MAX_MATCH_SIZE<=16)
        dest=BytesWriter()
        tmp0=[]
        for i in self.compress(src):
            if i[0]==0:
                tmp0.append(i[1])
                if len(tmp0)<16:
                    continue
            if len(tmp0)>0:
                dest.writeBitsFromInt32(0,1)
                dest.writeBitsFromInt32(len(tmp0)-1,4)
                for j in tmp0:
                    dest.writeByte(j)
                tmp0=[]
            if i[0]==1:
                dest.writeBitsFromInt32(1,1)
                dest.writeByte(i[1])
                dest.writeBitsFromInt32(i[2]-2,4)
                continue
        if len(tmp0)>0:
            dest.writeBitsFromInt32(0,1)
            dest.writeBitsFromInt32(len(tmp0)-1,4)
            for j in tmp0:
                dest.writeByte(j)
            tmp0=[]
        
        return dest.buffer
    # def decompressFromBytes(self,src:Union[Iterable[int],Iterator[int]])->bytearray:
    #     return bytearray(list(self.decompressIteratorFromBytes(SubByteReader(iter(src)))))

    def decompressFromBytes(self,src:Union[Iterable[int],Iterator[int]])->bytearray:
        """ compressToBytesで圧縮したデータを復元する。
            decompressを経由しない。
        """
        sw=self.SlidingWindow(self._sw_size)
        dest=bytearray()
        s=BytesIteratorReader(src if isinstance(src,Iterator) else iter(src))        
        while True:
            try:
                f=s.readBitsAsInt32(1)
                if f==0:
                    l=s.readBitsAsInt32(4)+1
                    for i in range(l):
                        d=s.readByte()
                        dest.append(d)
                        sw.push(d)
                elif f==1:
                    d0=s.readByte()
                    d1=s.readBitsAsInt32(4)
                    n=sw.gets(d0,d1+2)
                    dest.extend(n)
                    sw.pushs(n)
                else:
                    raise RuntimeError()
            except StopIteration:
                return dest
        raise RuntimeError()
    def decompressIteratorFromBytes(self,src:ABytesReader)->Iterator[int]:
        """ compressToBytesで圧縮したデータをIteraorで返却する。
        """
        class Iter(Iterator[int]):
            def __init__(self,sw_size:int,src:BytesIteratorReader):                
                self._sw=Lzss.SlidingWindow(sw_size)
                self._src=src
                self._co_state=0
                self._co_limit=0
                self._co_i=0
                self._co_d0=0
            def __next__(self):
                sw=self._sw
                src=self._src
                while True:
                    if self._co_state==0:
                        f=src.readBitsAsInt32(1)
                        if f==0:
                            self._co_state=10
                        elif f==1:
                            self._co_state=20
                        else:
                            raise RuntimeError()
                    if self._co_state==10:
                        self._co_limit=src.readBitsAsInt32(4)+1
                        self._co_i=0
                        self._co_state=11
                    if self._co_state==11:
                        d=src.readByte()
                        sw.push(d)
                        self._co_i=self._co_i+1
                        if self._co_i>=self._co_limit:
                            self._co_state=0
                        return d
                    if self._co_state==20:
                        self._co_d0=src.readByte()
                        self._co_i=0
                        self._co_limit=src.readBitsAsInt32(4)+2
                        self._co_state=21
                    if self._co_state==21:
                        d0=self._co_d0#+self._co_i
                        n=sw.get(d0)
                        self._co_i=self._co_i+1
                        sw.push(n)
                        if self._co_i>=self._co_limit:
                            self._co_state=0
                        return n
        # ラップ市内で直に使うようにする。じかに使う場合はAPIコールの直前でアライメントを揃える感じに
        # return Iter(self._sw_size,src)
        return Iter(self._sw_size,BytesIteratorReader.wrapByteReader(src))


    
        




#%%
#%%
# %%
