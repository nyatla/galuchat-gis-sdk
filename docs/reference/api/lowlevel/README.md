# Low-level API

[APIドキュメント](../README.md) / [ドキュメント索引](../../README.md)

## 目的

この文書は、アプリケーション側へ露出する低レベルAPIの入口である。

既存の Python Reader 実装は変更せず、まずはアプリケーションが依存する最小インタフェイスを整理する。

この段階で定義するインタフェイスは次の2つに限定する。

- [`IWgsMapset3Reader`](./IWgsMapset3Reader.md)
- [`IWordBookReader`](./IWordBookReader.md)

逆ジオコーダ本体、データセットローダ、GI01チャンクReader、DOM、Header、Chunk APIは、この文書では定義しない。

## 共通規約

### 座標

公開APIの座標引数は、次の順序に統一する。

```text
lon, lat
x, y
```

`lon, lat` はWGS84の浮動小数点経度緯度である。

```text
lon = 経度
lat = 緯度
```

`x, y` はWGSMapSet全体の整数グリッド座標である。

```text
x = ilon = round(lon * unitInvX)
y = ilat = round(lat * unitInvY)
```

`x` は経度方向、`y` は緯度方向である。

### 値

`IWgsMapset3Reader` が返すピクセル値は、地図データに格納された整数値である。

逆ジオコーディング用途では、通常この値を地名コードとして扱う。

```text
value = 0
  -> 未設定

value > 0
  -> IWordBookReader の code
```
