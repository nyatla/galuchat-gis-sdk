# IWordBookReader

地名コードから階層地名の `StringSet` を読むためのアプリケーション向けインタフェイス。

`StringSet` は1レコード分の階層文字列列である。要素数は `depth` と同じである。

## プロパティ

```python
class IWordBookReader(Protocol):
    @property
    def recordCount(self) -> int:
        ...

    @property
    def depth(self) -> int:
        ...
```

| プロパティ | 内容 |
| --- | --- |
| `recordCount` | 地名レコード数 |
| `depth` | 階層深度 |

## 地名読出し

```python
class IWordBookReader(Protocol):
    def readStringSetByCode(
        self,
        code: int,
    ) -> tuple[str, ...] | None:
        ...

    def readStringSetByIndex(
        self,
        index: int,
    ) -> tuple[str, ...]:
        ...
```

| メソッド | 内容 |
| --- | --- |
| `readStringSetByCode` | 地名コードから `StringSet` を読む |
| `readStringSetByIndex` | `GisWordBook` の0始まりindexから `StringSet` を読む |

コードとindexの対応は次の通り。

```text
code <= 0
  -> None

code > 0
  -> index = code - 1
```

`readStringSetByIndex` に範囲外indexを指定した場合は例外にする。

## 連続地名読出し

```python
class IWordBookReader(Protocol):
    def iterStringSetsByCodes(
        self,
        codes: Iterable[int],
    ) -> Iterator[tuple[str, ...] | None]:
        ...

    def iterStringSetsByIndices(
        self,
        indices: Iterable[int],
    ) -> Iterator[tuple[str, ...]]:
        ...
```

| メソッド | 内容 |
| --- | --- |
| `iterStringSetsByCodes` | 複数の地名コードから `StringSet` を逐次読む |
| `iterStringSetsByIndices` | 複数の0始まりindexから `StringSet` を逐次読む |

`iterStringSetsByCodes` は、入力 `codes` と同じ順序で結果を返す。各要素の規則は `readStringSetByCode` と同じである。

`iterStringSetsByIndices` は、入力 `indices` と同じ順序で結果を返す。各要素の規則は `readStringSetByIndex` と同じである。
