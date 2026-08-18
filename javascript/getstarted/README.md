# JavaScript Get Started

SDKに同梱された `javascript/galuchat.min.js` と共通データセットを使用するブラウザサンプルです。

SDKルートでHTTPサーバを起動します。

```bash
python3 -m http.server 8000
```

`http://localhost:8000/javascript/getstarted/` をブラウザで開いてください。`file://` では `fetch()` でのデータ読み込みが失敗する場合があります。

- `reverse-geocode/`: WGSMapSetとGisWordBookを使った逆ジオコード
- `getimage/`: WGSMapSet Readerでの矩形取得とCanvasへの画像描画
- `multizoom/`: 複数解像度のWGSMapSetを切り替えるズーム地図（JavaScript固有機能）

## 最小コード

次のコードは、東京駅付近の経緯度から行政区域コードと地名階層を取得します。SDKルートから配信した`javascript/getstarted/index.html`などに記述できます。

```html
<script src="../galuchat.min.js"></script>
<script>
(async () => {
  const load = async (url) =>
    new Uint8Array(await (await fetch(url)).arrayBuffer());
  const [mapBytes, wordbookBytes] = await Promise.all([
    load("../../datasets/jp-admin-n03/N03-20240101-grid-4096-1000.remap.wgsmapset.glc"),
    load("../../datasets/jp-admin-n03/N03-20240101.giswordbook"),
  ]);

  const map = Galuchat.GaluchatWGSMapSet3Reader.fromUint8Array(mapBytes);
  const wordbook = Galuchat.GaluchatGisWordBookReader.fromUint8Array(wordbookBytes);
  const result = new Galuchat.ReverseGeocoder(map, wordbook)
    .reverseGeocode(139.7671, 35.6812);
  console.log(result.code, result.path, result.name);
})();
</script>
```

マルチズームはJavaScript固有機能です。表示には`unitInv=100`、`1000`、`10000`のWGSMapSetを切り替えて使用し、地点のコードと地名は最高解像度のWGSMapSetと共通GisWordBookから取得します。JavaおよびPythonのGet Startedには収録しません。
