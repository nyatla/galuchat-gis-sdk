package jp.nyatla.galuchat.getstarted;

import java.nio.file.Files;
import java.nio.file.Path;

import jp.nyatla.galuchatJava.format.wgsmapset3.GaluchatWGSMapSet3Reader;

public final class ReadMapSet {
    private static final String MAPSET = "N03-20240101-grid-4096-1000.remap.wgsmapset.glc";

    private ReadMapSet() {
    }

    public static void main(String[] args) throws Exception {
        Path mapsetPath = ExamplePaths.input(args, 0, MAPSET);
        GaluchatWGSMapSet3Reader mapset = GaluchatWGSMapSet3Reader.fromBytes(
            Files.readAllBytes(mapsetPath));
        var bounds = mapset.getAreaOfWgs();

        System.out.printf("file: %s%n", mapsetPath);
        System.out.printf("unitInv: (%d, %d)%n", mapset.getUnitInvX(), mapset.getUnitInvY());
        System.out.printf("maps: %d%n", mapset.getNumOfMaps());
        System.out.printf(
            "bounds: lon %.3f..%.3f, lat %.3f..%.3f%n",
            bounds.west(), bounds.east(), bounds.south(), bounds.north());
    }
}
