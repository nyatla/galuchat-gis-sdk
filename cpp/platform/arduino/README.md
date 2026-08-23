# Arduino platform

Arduino向けC++サンプルを配置します。

- `reverse-geocoding`: N03データをFlash ROMへ組み込む逆ジオコーディング
- `reverse-geocoding-file`: N03の1/1000度版データをLittleFSから逐次読む逆ジオコーディング

現在のReaderはSTLと例外を利用するため、最初の対象はESP32等の比較的大きなボードです。
N03のMapSetとWordBookだけで約85KBあるため、Uno/Nano等の小容量AVRボードは対象外です。

各スケッチは同じディレクトリの`galuchat_bridge.hpp`から共通`src`を参照します。
Arduino IDEではライブラリの事前インストールや追加のインクルードパス指定をせず、
このディレクトリ以下の`.ino`を直接開いてコンパイルできます。
Arduino CLIとESP32 coreがある環境では、次のコマンドで両スケッチをコンパイルできます。

```sh
make -C cpp/platform/arduino
```

ボードを変更する場合は、例えば`FQBN=esp32:esp32:esp32s3`を指定します。
