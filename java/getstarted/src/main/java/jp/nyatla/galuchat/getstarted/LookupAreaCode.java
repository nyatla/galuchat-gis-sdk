package jp.nyatla.galuchat.getstarted;

import java.nio.file.Files;
import java.nio.file.Path;

import jp.nyatla.galuchatJava.format.wgsmapset3.GaluchatWGSMapSet3Reader;

public final class LookupAreaCode {
    private static final String MAPSET = "N03-20240101-grid-4096-1000.remap.wgsmapset.glc";
    private static final Point[] POINTS = {
        new Point("Imperial Palace", 139.7528, 35.6852),
        new Point("Tokyo Station", 139.7671, 35.6812),
        new Point("Shinjuku Station", 139.7006, 35.6896),
    };

    private LookupAreaCode() {
    }

    public static void main(String[] args) throws Exception {
        Path mapsetPath = ExamplePaths.input(args, 0, MAPSET);
        GaluchatWGSMapSet3Reader mapset = GaluchatWGSMapSet3Reader.fromBytes(
            Files.readAllBytes(mapsetPath));

        for (Point point : POINTS) {
            var code = mapset.readWgsPointf(point.lon, point.lat);
            System.out.printf(
                "%s: lon=%.4f, lat=%.4f, code=%s%n",
                point.label, point.lon, point.lat,
                code.isPresent() ? Integer.toString(code.get()) : "(outside)");
        }
    }

    private record Point(String label, double lon, double lat) {
    }
}
