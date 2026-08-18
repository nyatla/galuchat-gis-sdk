# Python Get Started

Python 3.11以降で、SDKに同梱されたソースを `PYTHONPATH` から直接参照します。

逆ジオコード:

```bash
PYTHONPATH=python/src python3 \
  python/getstarted/reverse_geocode_imperial_palace.py \
  datasets/jp-admin-n03/N03-20240101-grid-4096-1000.remap.wgsmapset.glc \
  datasets/jp-admin-n03/N03-20240101.giswordbook
```

PNG描画にはPillowが必要です。

```bash
PYTHONPATH=python/src python3 \
  python/getstarted/render_funabashi_vga.py \
  datasets/jp-admin-n03/N03-20240101-grid-4096-1000.remap.wgsmapset.glc \
  work/funabashi-vga.png
```

SDKはPythonパッケージのインストール機能を持ちません。Pillowは利用側の環境で用意してください。

## 最小コード

次のコードは、東京駅付近の経緯度から行政区域コードと地名階層を取得します。SDKルートから`PYTHONPATH=python/src python3 example.py`として実行できます。

```python
from galuchat.api.lowlevel import GisWordBookReaderAdapter, WgsMapset3ReaderAdapter

mapset = WgsMapset3ReaderAdapter.fromFile(
    "datasets/jp-admin-n03/N03-20240101-grid-4096-1000.remap.wgsmapset.glc"
)
wordbook = GisWordBookReaderAdapter.fromFile(
    "datasets/jp-admin-n03/N03-20240101.giswordbook"
)

code = mapset.readWgsPoint(139.7671, 35.6812)
path = wordbook.readStringSetByCode(code) if code is not None else None
print("code:", code)
print("path:", path)
```
