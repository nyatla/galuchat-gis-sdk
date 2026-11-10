# 英字表示言語パック

[English](en.md) | 日本語

[en rev1言語パック（29.36 MiB）](https://github.com/nyatla/galuchat-gis-sdk/releases/download/v0.2.7/galuchat-languagepack-en-rev1.zip)には、46件の地図データセットとe-Statの追加4階層辞書に対応する表示辞書を収録しています。`rev1`は言語パック独自の改訂番号であり、SDKのバージョンや元の地図ZIPの改訂番号とは独立です。

## 使い方

1. [データセットガイド](../../datasets/README.ja.md)に記載された地図ZIPと言語パックZIPをダウンロードします。
2. 言語パック内の`galuchat-languagepack-en/datasets/<地図ZIP名から.zipを除いた名前>/`を開きます。`revN`を含む地図ZIPの名前とディレクトリ名を一致させてください。e-Statの追加4階層辞書には`subdiv`のZIP名のディレクトリを使います。
3. 地図ファイルはそのまま使い、そのディレクトリの`.en.giswordbook`を元の辞書の代わりにSDKで読み込みます。同じディレクトリの`NOTICE.md`で出典・利用条件を確認してください。

例として、SDK同梱のN03-2026地図には、言語パック内の`datasets/jp-2026-mlit-go-jp-n03-adm-rev1/N03-20260101.en.giswordbook`が対応します。[Python Get Started](../../python/getstarted/README.md)の`GisWordBookReaderAdapter.fromFile(...)`に渡す辞書パスを、展開したこのファイルのパスに変更します。WGSMapSetのパスはそのまま使用します。他言語のReaderも辞書のパスまたはバイト列を指定できます。

言語パック内の`README.md`に47件の対応元ZIPと収録ファイルの一覧があります。各ディレクトリの`.en.names.csv`には原文と採用表記の対応が記録されています。辞書はUTF-8形式で、表示文字列に印字可能ASCIIを使用します。名称には正式英語名、公表ローマ字、転写、説明訳などがあり、すべてが正式英語訳という意味ではありません。コード順とスロット構造は対応元ZIPと一致します。
