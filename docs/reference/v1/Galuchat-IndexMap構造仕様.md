# IndexMap走査順付け仕様書

## 1. 目的と背景

Galuchat画像圧縮コーデックにおいては、ブロック内の画素データを加工する際に、ランレングス符号化 (RLE) などの加工效果を最大化するため、「IndexMap」と呼ばれる特殊な走査順を利用する。

本文書は、Galuchat内で実際に使用されているIndexMapの構造と定義を詳細に文書化することを目的とする。

## 2. 用語定義と記号

- **IndexMap** : 2次元のラスタの順序を、1次元の配列として利用するための変換テーブル
- **map(i)** : 1次元index `i` を走査先の第何位置に対応させる関数
- **unmap(i)** : `map()` の逆関数
- **resolution** : ブロックの大きさ (NxN)

## 3. IndexMap構造の原理

IndexMapは、2次元の画像ブロックを、1次元のデータとして処理する際にの走査順を表現するためのマッピングである。`map()`/`unmap()` 関数を通じて、行列上のインデックスの変換を可逆に行う。

複数のIndexMapを連鎖した「ChaindIndexMap」として利用される場合もあり、その場合、`map()` は連鎖順の各変換を順に適用した結果を返す。

## 4. map()処理の定義

以下に示す各IndexMapは、共通して次の「元の並び順（ラスタスキャン）」を基準として変換を行う。これは上から下、左から右に順に画素をスキャンしたものである。

### 4.1 ZigzagIndexMap

- 偶数行は左→右、奇数行は右→左 にジグザグに走査
- 擬似コード:
```python
def map(index):
    size = self._size
    y = index // size
    x = index % size
    if y % 2 == 0:
        return x + y * size
    else:
        return (size - 1 - x) + y * size
```

- 偶数行は左→右、奇数行は右→左 にジグザグに走査
- 例（4x4）:

```
 0  1  2  3     →     0  1  2  3
 4  5  6  7           7  6  5  4
 8  9 10 11           8  9 10 11
12 13 14 15          15 14 13 12
```

### 4.2 MirrorIndexMap

- x_mirror: 水平方向のミラー（左右反転）
- y_mirror: 垂直方向のミラー（上下反転）
- 擬似コード:
```python
def map(index):
    size = self._size
    x = (size - 1 - index % size) if self._x_mirror else index % size
    y = (size - 1 - index // size) if self._y_mirror else index // size
    return x + y * size
```

- x\_mirror: 水平方向のミラー（左右反転）

- y\_mirror: 垂直方向のミラー（上下反転）

- 例（4x4, x\_mirror=True, y\_mirror=False）:

```
 0  1  2  3     →     3  2  1  0
 4  5  6  7           7  6  5  4
 8  9 10 11          11 10  9  8
12 13 14 15          15 14 13 12
```

- 例（4x4, x\_mirror=False, y\_mirror=True）:

```
 0  1  2  3     →    12 13 14 15
 4  5  6  7           8  9 10 11
 8  9 10 11           4  5  6  7
12 13 14 15           0  1  2  3
```

### 4.3 TransposeIndexMap

- 転置：行列の x, y 軸を入れ替える
- 擬似コード:
```python
def map(index):
    size = self._size
    x = index // size
    y = index % size
    return x + y * size
```

- 転置：行列の x, y 軸を入れ替える

- 例（3x3）:

```
 0  1  2     →      0  3  6
 3  4  5            1  4  7
 6  7  8            2  5  8
```

### 4.4 ChaindIndexMap

- 複数のIndexMapを連鎖した構造。
- それぞれのIndexMapを順番に適用した結果が出力される。
- 使用されている具体的な組み合わせは以下の通り：

#### 1. Mirror(x) → Zigzag
```
変換前     → Mirror(x)     → Zigzag
 0  1  2  3     3  2  1  0     3  2  1  0
 4  5  6  7     7  6  5  4     4  5  6  7
 8  9 10 11    11 10  9  8    11 10  9  8
12 13 14 15    15 14 13 12    12 13 14 15
```

#### 2. Zigzag → Transpose
```
変換前     → Zigzag         → Transpose
 0  1  2  3     0  1  2  3     0  7  8 15
 4  5  6  7     7  6  5  4     1  6  9 14
 8  9 10 11     8  9 10 11     2  5 10 13
12 13 14 15    15 14 13 12     3  4 11 12
```

#### 3. Mirror(y) → Zigzag → Transpose
```
変換前     → Mirror(y)      → Zigzag        → Transpose
 0  1  2  3    12 13 14 15    12 13 14 15     12 11  4  3
 4  5  6  7     8  9 10 11    11 10  9  8     13 10  5  2
 8  9 10 11     4  5  6  7     4  5  6  7     14  9  6  1
12 13 14 15     0  1  2  3     3  2  1  0     15  8  7  0
```

## 5. unmap()処理の定義

各IndexMapは map() の逆操作として unmap() を持ち、継続性のある走査の復元を可能にする。

## 6. 実装上の注意点

- ChaindIndexMapの連鎖順は定順であり、順番を反転すると動作が異なる
- resolution の不適合を防ぐため、NxNのブロック形式を前提とする
- 一意性のため map/unmap は正確な反対関数でなければならない

## 7. 使用されているIndexMapモード一覧

以下はGaluchatコーデックにおいて定義済みのIndexMapモードである。

- `RLE_MODE_Zigzag`: ZigzagIndexMap
- `RLE_MODE_Zigzag_MH`: Mirror(x)+Zigzag
- `RLE_MODE_Zigzag_T`: Zigzag+Transpose
- `RLE_MODE_Zigzag_T_MV`: Mirror(y)+Zigzag+Transpose

これらのモードはRLE圧縮における走査順を指定するために使用される。
非RLE圧縮形式（RawCodecなど）ではIndexMapは使用されない。

