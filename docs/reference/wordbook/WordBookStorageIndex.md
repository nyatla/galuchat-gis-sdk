# WordBook 格納仕様ドキュメント

[ドキュメント索引](../README.md)

この仕様は、次の文書に分割する。

| 文書 | 内容 |
| --- | --- |
| [WordBookStorageFormat.md](WordBookStorageFormat.md) | `WordBook` 全体の包括仕様 |
| [GisWordBookStorageFormat.md](GisWordBookStorageFormat.md) | `GisWordBook` 全体の包括仕様 |
| [TM00TokenMapChunk.md](TM00TokenMapChunk.md) | `TM00` TokenMap チャンク仕様 |
| [TT00TextTableChunk.md](TT00TextTableChunk.md) | `TT00` TextTable チャンク仕様 |
| [TI00HierarchicalIndexChunk.md](TI00HierarchicalIndexChunk.md) | `TI00` HierarchicalIndex チャンク仕様 |

[WordBookBitstreamDesign.md](WordBookBitstreamDesign.md)は、符号化方式の設計資料である。格納形式の定義は上表の仕様を優先する。

旧 `WordBook` / `NM00` 単体チャンク仕様は廃止する。
現行仕様では `WordBook` が `TM00` と `TT00` を包括する。
