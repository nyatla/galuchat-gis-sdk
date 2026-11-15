# 英字表示言語パック

[English](en.md) | 日本語

[en rev2言語パック（29.37 MiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.8/galuchat-languagepack-en-rev2.zip)は、46件の地図データセットとe-Statの追加4階層辞書に対応します。`rev2`は言語パック独自の改訂番号です。

## 使い方

1. [データセットガイド](../../datasets/README.ja.md)に記載された地図ZIPと言語パックZIPをダウンロードします。
2. 言語パック内の`galuchat-languagepack-en/datasets/<対応元ZIP名から.zipを除いた名前>/`を開きます。`revN`まで一致させてください。e-Statの追加4階層辞書は`subdiv` ZIP名を使います。
3. 地図はそのまま使い、元の辞書の代わりに`.en.giswordbook`を読み込みます。出典と利用条件は同じディレクトリの`NOTICE.md`を確認してください。

実装例：[Python Get Started](../../python/getstarted/README.md)の辞書パスを`.en.giswordbook`に変更します。

辞書はUTF-8形式で、表示名は印字可能ASCIIです。正式英語名とは限りません。原文との対照表は各ディレクトリの`.en.names.csv`、対応元ZIPの一覧はパック内の`README.md`を参照してください。
