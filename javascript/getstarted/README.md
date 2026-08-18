# JavaScript Get Started

SDKに同梱された `javascript/galuchat.min.js` と共通データセットを使用するブラウザサンプルです。

SDKルートでHTTPサーバを起動します。

```bash
python3 -m http.server 8000
```

`http://localhost:8000/javascript/getstarted/` をブラウザで開いてください。`file://` では `fetch()` でのデータ読み込みが失敗する場合があります。

- `reverse-geocode/`: WGSMapSetとGisWordBookを使った逆ジオコード
- `getimage/`: WGSMapSet Readerでの矩形取得とCanvasへの画像描画

マルチズームはJavaScriptスペシャル機能のため、標準SDKには含みません。
