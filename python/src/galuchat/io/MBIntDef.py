from ..math import Limit

class MBIntDef:
    """ MBUINT仕様
        モード1 - バイト値が多い場合最大30bit
        -       prefix  値幅      最小    最大

        1バイト  -       252        0        251
        2バイト 255      256        252      507        8
        3バイト 254      65536      508      66043      8+8     1バイト目 254
        4バイト 253      16777216   66044    16843259   8+8+8   1バイト目 253
        5バイト 252      4294967296 16843260 4311810555 8+8+8+8 1バイト目 252

        MBINT仕様
        1バイト目の1ビット目を符号として、値範囲を以下に修正する。
        1バイト  -       124        0        123
        2バイト 127      256        124      379        8
        3バイト 126      65536      380      65915      8+8
        4バイト 125      16777216   65916    16843131   8+8+8
        5バイト 124      4294967296 16843132 4311810427 8+8+8+8


        

        

    """
    INT1_MIN=Limit.INT8MIN
    INT1_MAX=Limit.INT8MAX
    INT2_MIN=Limit.INT16MIN
    INT2_MAX=Limit.INT8MAX
    INT3_MIN=Limit.INT24MIN
    INT3_MAX=Limit.INT24MAX
    INT4_MIN=Limit.INT32MIN
    INT4_MAX=Limit.INT32MAX

    MUINT1_BASE  =0
    MUINT2_BASE   =MUINT1_BASE+252
    MUINT3_BASE   =MUINT2_BASE+0xff+1
    MUINT4_BASE   =MUINT3_BASE+0xffff+1
    MUINT5_BASE   =MUINT4_BASE+0xffffff+1

    MINT1_BASE  =0
    MINT2_BASE   =MINT1_BASE+124
    MINT3_BASE   =MINT2_BASE+0xff+1
    MINT4_BASE   =MINT3_BASE+0xffff+1
    MINT5_BASE   =MINT4_BASE+0xffffff+1


    @classmethod
    def sizeOfMbUint(cls,n:int)->int:
        if n<cls.MUINT2_BASE:
            return 1
        elif n<cls.MUINT3_BASE:
            return 2
        elif n<cls.MUINT4_BASE:
            return 3
        elif n<cls.MUINT5_BASE:
            return 4
        elif n<cls.MUINT5_BASE+0xffffffff:
            return 5
        raise RuntimeError()