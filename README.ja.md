# Galuchat GIS SDK

[English](README.md) | 日本語

Galuchat GIS SDK は、セグメント画像格納方式 Galuchat で生成されたGISデータ（WGSMapSet）を利用するためのSDKです。経緯度座標から地点に対応するコード番号や地名を取得する、逆ジオコーディング機能の実装を支援します。

本SDKと付属データを使用することで、ネットワーク上のGISサービスや外部データベースに依存せず、指定した地点に対応するコード番号や地名、および指定範囲のコードラスタを取得できます。

ブラウザやローカルアプリケーションにGISデータを保持し、オフラインで動作する逆ジオコーディングシステムを構成できます。外部サービスに依存しないため、組み込み機器やモバイル環境への応用も可能です。

## データ例

次の画像は、習志野市付近を中心として実際のWGSMapSetをドットバイドットで描画した例です。青色は海面などの未設定領域、その他の色は異なる地域コードを表し、色自体に意味はありません。

<table>
  <tr>
    <th>行政区域データ（unitInv=1000）</th>
    <th>行政区域・小地区統合データ（unitInv=10000）</th>
  </tr>
  <tr>
    <td><a href="docs/image/jp-admin-n03-unit-inv-1000.png"><img src="docs/image/jp-admin-n03-unit-inv-1000.png" alt="習志野市付近の行政区域データ"></a></td>
    <td><a href="docs/image/jp-gis-estat-integrated-unit-inv-10000.png"><img src="docs/image/jp-gis-estat-integrated-unit-inv-10000.png" alt="習志野市付近の行政区域・小地区統合データ"></a></td>
  </tr>
</table>

解像度は境界形状の細かさ、領域粒度はコードが表す市区町村・町丁・小地区などの単位です。高解像度でも領域粒度が細かくなるとは限らないため、用途に応じてデータセットを選択します。

収録データの比較、全レンダリング例、ファイルサイズは[データセットガイド](datasets/README.ja.md)で確認できます。

## データ構造

Galuchat GIS SDKで使用するデータは、主にWGSMapSetとGisWordBookの2つから構成されます。

WGSMapSetは、領域の識別子であるコード番号を画素値として持つラスタ画像を、Galuchatの空間分割格納方式によって格納したデータです。

元となるデータは、地域または領域コードごとにベクトル形式で表現された領域情報を合成・レンダリングして生成した高解像度ラスタ画像です。WGSMapSetでは、この画像の座標軸を経度・緯度に対応させ、Galuchat形式へ変換して格納します。

GisWordBookは、コード番号から順序付きの地名階層を復元するためのデータです。内部では文字列辞書と階層インデックスを組み合わせて格納します。

逆ジオコーディングでは、まず経緯度座標をWGSMapSetによってコード番号へ変換し、そのコード番号をGisWordBookによって対応する地名情報へ変換します。

## SDKの機能の概要

本SDKは、経緯度から地名を得る逆ジオコーディング機能を中心に、以下の機能を提供します。

- 経度・緯度（lon, lat）から行政区域や小地区のコードを取得する。
- 地域コードを都道府県、市区町村、町丁などの地名階層へ変換する。
- 指定範囲をラスタ画像として読み出す。
- JavaScript・Java・Python・C++で共通のGISデータを使用する。
- データとReaderをローカルに配置して利用する。

## はじめる

SDKはパッケージマネージャを前提としないファイルセットです。利用する言語の実装と、`datasets/`のmap・GisWordBookを直接参照します。

- [JavaScript Get Started](javascript/getstarted/README.md)
- [Java Get Started](java/getstarted/README.md)
- [Python Get Started](python/getstarted/README.md)
- [C++/Arduino Get Started](cpp/README.md)

## SDKの構成

```text
javascript/                 ブラウザ用IIFE実装とサンプル
java/                       外部依存のないReader jarとサンプル
python/                     Pythonソースとサンプル
cpp/                        C++17 Reader、Arduinoライブラリ、サンプル
datasets/                   4言語で共有するGISデータ
docs/image/                 データセットのレンダリング例
docs/reference/             公開APIと現行ファイル形式仕様
VERSION                     SDK自身のバージョン
```

JavaScript・Java・Python・C++は同格の実行環境です。各言語の成果物にバージョン番号ディレクトリは設けず、SDKに収録した組み合わせをそのまま利用します。

## 収録データ

| dataset id | 内容 |
| --- | --- |
| `jp-admin-n03-2024` | 国土数値情報 行政区域データ（2024年） |
| `jp-admin-n03-2025` | 国土数値情報 行政区域データ（2025年） |
| `jp-admin-n03-2026` | 国土数値情報 行政区域データ（2026年） |
| `jp-estat-r2ka-2020` | 令和2年国勢調査 町丁・字等境界データ |
| `jp-gis-estat-integrated` | 行政区域とe-Stat小地区の統合データ |
| `world-geoboundaries-cgaz` | geoBoundaries CGAZ世界行政境界 |

mapの解像度とWordBookの文字コードは[データセットガイド](datasets/README.ja.md)にまとめています。出典、加工内容、利用条件は各datasetの`NOTICE.md`を確認してください。

## ファイル形式

現在のSDKは、WGSMap/3、WGSMapSet/3、GI01 image chunk、GisWordBook/0に対応します。画素値`0`は未設定領域、正の値は同じdatasetに収録されたGisWordBookの1始まりの地名コードです。

公開APIとファイル形式の詳細は[技術仕様](docs/reference/README.md)を参照してください。これらの文書は`galuchat-core`を正本としてSDK製造時に同期されます。

## このリポジトリについて

README、Get Startedの説明、データガイド、NOTICE、VERSIONはSDK自身が管理します。実装ソース、ビルド成果物、GLC、GisWordBookは、`galuchat-core`の同期工程によって必要なものだけが更新されます。

## ライセンス

Galuchatのソフトウェアコードと文書は、特に記載がない限り[Apache License 2.0](LICENSE)で提供します。収録データセットはApache License 2.0の対象ではなく、データセットごとの利用条件が適用されます。詳細は[第三者成果物とデータの表示](THIRD_PARTY_NOTICES.md)および各データセットの`NOTICE.md`を確認してください。

契約上の保証、補償、サポート、追加の特許保証、または異なる利用条件を必要とする組織向けに、[別途商用ライセンス](COMMERCIAL-LICENSING.md)を提供できる場合があります。Apache License 2.0による利用に個別契約は必要ありません。
