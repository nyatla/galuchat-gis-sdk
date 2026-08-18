package jp.nyatla.galuchat.getstarted;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import javax.imageio.ImageIO;

import jp.nyatla.galuchatJava.format.wgsmapset3.GaluchatWGSMapSet3Reader;
import jp.nyatla.galuchatJava.j2se.MapRender;
import jp.nyatla.galuchatJava.math.rect.IntGisRect;

public final class RenderFunabashi {
    private static final String MAPSET = "N03-20240101-grid-4096-1000.remap.wgsmapset.glc";
    private static final double FUNABASHI_LON = 139.9825;
    private static final double FUNABASHI_LAT = 35.6947;
    private static final int WIDTH = 640;
    private static final int HEIGHT = 480;

    private RenderFunabashi() {
    }

    public static void main(String[] args) throws Exception {
        Path mapsetPath = ExamplePaths.input(args, 0, MAPSET);
        Path output = args.length > 1 ? Path.of(args[1]) : Path.of("funabashi-vga.png");
        GaluchatWGSMapSet3Reader mapset = GaluchatWGSMapSet3Reader.unpack(
            Files.readAllBytes(mapsetPath));

        int centerX = (int) Math.round(FUNABASHI_LON * mapset.getUnitInvX());
        int centerY = (int) Math.round(FUNABASHI_LAT * mapset.getUnitInvY());
        var target = new IntGisRect(
            centerX - WIDTH / 2,
            centerY - HEIGHT / 2,
            WIDTH,
            HEIGHT);
        var raster = mapset.readWgsRect(target);
        var image = new MapRender(true).toMap(raster, List.of());

        Path parent = output.toAbsolutePath().getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }
        ImageIO.write(image, "PNG", output.toFile());
        System.out.printf("wrote: %s (%dx%d)%n", output, image.getWidth(), image.getHeight());
    }
}
