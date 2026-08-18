#%%
from typing import List, Tuple,Generator,Iterable,Iterator,Union

class Rle:
    """ Int配列をRleエンコードします。
        配列は[[size,value],...]の形式です。
    """
    @classmethod
    def encode(cls,data: Iterable[int]) -> Generator[Tuple[int, int], None, None]:
        count = 1
        data_iter = iter(data)
        prev = next(data_iter)
        for current in data_iter:
            if prev == current:
                count += 1
            else:
                yield (count, prev)
                count = 1
            prev = current
        yield (count,prev)
    @classmethod
    def decode(cls,encoded: List[Tuple[int, int]]) -> List[int]:
        decoded: List[int] = []
        for count, char_code in encoded:
            decoded.extend([char_code] * count)
        return decoded

    @classmethod
    def encodeBytearray(cls,data:bytearray)->bytearray:
        """ UINT8[]をRLEエンコードする.
        """
        r=bytearray()
        for i in cls.encode(data):
            r.extend(i)
        return r    
    @classmethod
    def decodeBytearray(cls,encoded:Iterator[int],length:int=None)->bytearray:
        """ Rle[UINT8]をデコードする。
        """
        decoded=bytearray()
        l=0
        try:
            while (length is None) or l<length:
                count=next(encoded)
                code=next(encoded)
                decoded.extend([code] * count)
                l+=count
        except StopIteration:
            assert(l==length)
        return decoded 
    @classmethod
    def decodeBytearrayA(cls,encoded:bytearray,length:int=0x7fffffff)->bytearray:
        """ UINT8[]へデコードする。
        """
        return cls.decodeBytearray(iter(encoded),length)
    
#%%

# %%
