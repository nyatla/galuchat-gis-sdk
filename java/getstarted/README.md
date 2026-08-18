# Java Get Started

Java 20と同梱の `galuchat-java-core` jarを直接使用するサンプルです。
SDKルートで次を実行してください。

```bash
mkdir -p work/java-getstarted
javac --release 20 \
  -cp java/galuchat-java-core.jar \
  -d work/java-getstarted \
  $(find java/getstarted/src/main/java -name '*.java')
```

実行例:

```bash
java -cp java/galuchat-java-core.jar:work/java-getstarted \
  jp.nyatla.galuchat.getstarted.ReadMapSet \
  datasets/jp-admin-n03/N03-20240101-grid-4096-1000.remap.wgsmapset.glc

java -cp java/galuchat-java-core.jar:work/java-getstarted \
  jp.nyatla.galuchat.getstarted.ReverseGeocode \
  datasets/jp-admin-n03/N03-20240101-grid-4096-1000.remap.wgsmapset.glc \
  datasets/jp-admin-n03/N03-20240101.giswordbook
```

ほかに `LookupAreaCode` と `RenderFunabashi` を収録しています。

## 最小コード

次のコードは、東京駅付近の経緯度から行政区域コードと地名階層を取得します。SDKルートをカレントディレクトリとして実行する想定です。

```java
import java.nio.file.Files;
import java.nio.file.Path;

import jp.nyatla.galuchatJava.format.wgsmapset3.GaluchatWGSMapSet3Reader;
import jp.nyatla.galuchatJava.wordbook.GaluchatGisWordBookReader;

public class Main {
    public static void main(String[] args) throws Exception {
        var map = GaluchatWGSMapSet3Reader.unpack(Files.readAllBytes(Path.of(
            "datasets/jp-admin-n03/N03-20240101-grid-4096-1000.remap.wgsmapset.glc")));
        var wordbook = GaluchatGisWordBookReader.fromFile(Path.of(
            "datasets/jp-admin-n03/N03-20240101.giswordbook"));

        var code = map.readWgsPointf(139.7671, 35.6812);
        System.out.println("code: " + code);
        System.out.println("path: " + code.flatMap(wordbook::readStringSetByCode));
    }
}
```

SQLite/JDBIバインドはJavaスペシャル機能であり、標準SDKには含みません。
