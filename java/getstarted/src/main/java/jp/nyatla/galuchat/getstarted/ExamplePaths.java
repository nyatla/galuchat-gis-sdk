package jp.nyatla.galuchat.getstarted;

import java.nio.file.Files;
import java.nio.file.Path;

final class ExamplePaths {
    private ExamplePaths() {
    }

    static Path input(String[] args, int index, String fileName) {
        if (args.length > index) {
            return Path.of(args[index]);
        }
        Path local = Path.of("data", fileName);
        if (Files.isRegularFile(local)) {
            return local;
        }
        return Path.of("getstarted", "data", fileName);
    }
}
