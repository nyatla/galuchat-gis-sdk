# カタール自治体区域（2015年国勢調査付属境界）

[English](qa-2015-data-gov-qa-npc-od-c0-00621-adm1-rev1.md) | 日本語

[データセット目次に戻る](../../datasets/README.ja.md)

## 概要

採用した原典自治体面が表すカタールの範囲。原典に収録された島嶼・飛地を含む。 2015年国勢調査に付属する自治体境界。統計年は2015年、公式ポータルのデータ更新日は2025-06-02。境界図形自体の基準日は未確認であり、2015年・2025年・取得年のいずれとも断定しない。

## 区域数

辞書コード単位で **8区域** を収録します。Municipality（自治体）8区域。国直下の1段階の区域階層。 対象範囲と時点の詳細はZIP内の`data-spec.md`を参照してください。

## ダウンロード

[qa-2015-data-gov-qa-npc-od-c0-00621-adm1-rev1.zipをダウンロード（70.0 KiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.4/qa-2015-data-gov-qa-npc-od-c0-00621-adm1-rev1.zip)

このリンクはv0.2.4の公開後に利用できます。ZIPはローカルの`release/`に作成済みです。

## 地図の解像度とサイズ

| unitInv | 南北方向の画素間隔の目安 | WGSMapSetサイズ |
| ---: | ---: | ---: |
| 100 | 約1.1 km | 0.9 KiB |
| 1000（標準） | 約111 m | 6.6 KiB |
| 10000 | 約11 m | 57.1 KiB |

## 辞書

| GisWordBookの文字コード | サイズ |
| --- | ---: |
| UTF-8 | 0.4 KiB |
| UTF-16LE | 0.4 KiB |

同梱の`names.csv`で辞書コードと原典の識別子・名称を照合できます。地図と辞書は同じZIPから選んでください。

### GisWordBookの構造

各レコードは固定1スロットのStringSetです。

| 位置 | 意味 | 空値 |
| ---: | --- | --- |
| 1 | Municipality（自治体）の英語名称municipality。 | 不可 |

実データ例（辞書コード`1`）：

```json
["Al-Daayen"]
```

地図の非ゼロ値が辞書コードです。`0`は背景で、辞書レコードを指しません。空スロットがある場合も位置を詰めません。

## 描画例

<a href="../../docs/image/qa-2015-data-gov-qa-npc-od-c0-00621-adm1-unit-inv-1000.png"><img src="../../docs/image/qa-2015-data-gov-qa-npc-od-c0-00621-adm1-unit-inv-1000.png" alt="Doha付近のカタール自治体区域（2015年国勢調査付属境界）" width="640"></a>

Doha付近を`unitInv=1000`で描画しました。青色は背景、その他の色は区域コードの区別を示し、色自体に別の意味はありません。

## ライセンスと利用条件

原典：[原典](https://www.data.gov.qa/explore/dataset/distribution-of-business-establishments-and-employees-by-municipalities-according-to-census-2015/)。

原典のライセンス・利用条件：**CC BY 4.0**（[規約](https://creativecommons.org/licenses/by/4.0/)）。ZIP内の`NOTICE.md`に出典、適用条件、帰属表示および加工内容を記録しています。

### 商用利用・許諾申請（参考）

原典が示すCC BY 4.0は、条件に従う商用利用を認めています。確認した資料には、この範囲での個別許諾申請の指定はありません。用途に応じて現行の原典条件とZIP内のNOTICE.mdを確認してください。 これは参考情報であり、正式な利用許諾や法的判断を示すものではありません。

### 出典・加工・承認表示

ZIP内の`NOTICE.md`に記載した出典・加工表示を維持してください。この加工データを原典提供者の公式・公認・推奨製品として表示しません。

## 利用上の注意

同じZIPから用途に合う地図1つとGisWordBook1つを選びます。サイズはZIP内ファイルの実サイズ、画素間隔は概算です。区域範囲、コード対応、制約はZIP内の原典文書を確認してください。
