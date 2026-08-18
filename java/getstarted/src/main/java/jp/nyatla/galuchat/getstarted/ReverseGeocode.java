package jp.nyatla.galuchat.getstarted;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import jp.nyatla.galuchatJava.format.wgsmapset3.GaluchatWGSMapSet3Reader;
import jp.nyatla.galuchatJava.wordbook.GaluchatGisWordBookReader;

public final class ReverseGeocode {
    private static final String MAPSET = "N03-20240101-grid-4096-1000.remap.wgsmapset.glc";
    private static final String WORDBOOK = "N03-20240101.giswordbook";
    private static final Point[] POINTS = {
        new Point("Imperial Palace", 139.7528, 35.6852),
        new Point("Tokyo Station", 139.7671, 35.6812),
        new Point("Shinjuku Station", 139.7006, 35.6896),
    };

    private ReverseGeocode() {
    }

    public static void main(String[] args) throws Exception {
        Path mapsetPath = ExamplePaths.input(args, 0, MAPSET);
        Path wordbookPath = ExamplePaths.input(args, 1, WORDBOOK);
        GaluchatWGSMapSet3Reader mapset = GaluchatWGSMapSet3Reader.unpack(
            Files.readAllBytes(mapsetPath));
        GaluchatGisWordBookReader wordbook = GaluchatGisWordBookReader.fromFile(wordbookPath);

        System.out.printf(
            "mapset: unitInv=(%d, %d), maps=%d%n",
            mapset.getUnitInvX(), mapset.getUnitInvY(), mapset.getNumOfMaps());
        System.out.printf(
            "wordbook: records=%d, depth=%d%n%n",
            wordbook.getRecordCount(), wordbook.getDepth());

        for (Point point : POINTS) {
            var code = mapset.readWgsPointf(point.lon, point.lat);
            List<String> path = code.isPresent()
                ? wordbook.readStringSetByCode(code.get()).orElse(List.of())
                : List.of();
            System.out.printf("%s: lon=%.4f, lat=%.4f%n", point.label, point.lon, point.lat);
            System.out.printf("  code: %s%n", code.isPresent() ? code.get() : "(not found)");
            System.out.printf("  path: %s%n", formatPath(path));
        }
    }

    private static String formatPath(List<String> path) {
        String joined = path.stream()
            .filter(component -> !component.isEmpty())
            .reduce((left, right) -> left + " / " + right)
            .orElse("");
        return joined.isEmpty() ? "(not found)" : joined;
    }

    private record Point(String label, double lon, double lat) {
    }
}
