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
SQLite/JDBIバインドはJavaスペシャル機能であり、標準SDKには含みません。
