from typing import List
from .Limit import Limit

class RgbColor:
    """ [0,255]の値空間でRGBカラーを定義します。

    """
    def __init__(self,r:int,g:int,b:int):
        self.value=(r,g,b)
    @property
    def value24(self)->int:
        v=self.value
        return v[0]<<16 | v[1]<<8 | v[0]
    @classmethod
    def hsvColorMap(cls,h:float=1.0, s:float=1.0, v:int=1.0,hdiv:int=16):
        htbl=[(h*i)/hdiv for i in range(hdiv)]
        return [RgbColor.fromHsvf(i,s,v) for i in htbl]
    @classmethod
    def gsColorMap(cls,v:int)->"RgbColor":
        return RgbColor(v,v,v)


    @classmethod
    def fromHsvf(cls,h:float, s:float, v:float):
        r = v
        g = v
        b = v
        if s > 0.0:
            h *= 6.0
            i = int(h)
            f = h - i
            
            if i == 0:
                g *= 1 - s * (1 - f)
                b *= 1 - s
            elif i == 1:
                r *= 1 - s * f
                b *= 1 - s
            elif i == 2:
                r *= 1 - s
                b *= 1 - s * (1 - f)
            elif i == 3:
                r *= 1 - s
                g *= 1 - s * f
            elif i == 4:
                r *= 1 - s * (1 - f)
                g *= 1 - s
            elif i == 5:
                g *= 1 - s
                b *= 1 - s * f

        # 0-1 の範囲に収まる float 値を 0-255 の整数に変換
        return RgbColor(int(r * 255),int(g * 255),int(b * 255)) 
    

def isPowOf2(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def toBitWidth(n:int)->int:
    """ nを格納可能な2^nのビットサイズを返します。
    """
    if n<=2:
        return 1
    elif n<=4:
        return 2
    elif n<=16:
        return 4
    elif n<=256:
        return 8
    else:
        raise RuntimeError()

# def transpose(matrix: List[List[int]]) -> List[List[int]]:
#     """ 2次元マトリクスを転置します。
#     """
#     if not matrix:
#         return []
#     num_rows = len(matrix)
#     num_cols = len(matrix[0])
#     transposed = [[0 for _ in range(num_rows)] for _ in range(num_cols)]
#     for i in range(num_rows):
#         for j in range(num_cols):
#             transposed[j][i] = matrix[i][j]
#     return transposed


