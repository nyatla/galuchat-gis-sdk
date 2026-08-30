#include <chrono>
#include <cstdio>
#include <iomanip>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include "galuchat/gis_wordbook_reader.hpp"
#include "galuchat/std_file_reader.hpp"
#include "galuchat/wgsmap3_reader.hpp"

namespace {

constexpr const char* DEFAULT_MAPSET =
    "N03-20240101-grid-4096-1000.remap.wgsmapset.glc";
constexpr const char* DEFAULT_WORDBOOK = "N03-20240101.giswordbook";
constexpr size_t FILE_BUFFER_SIZE = 4096;

std::string joinPlaceName(const std::vector<std::string>& components) {
    std::string result;
    for (const std::string& component : components) {
        if (component.empty()) {
            continue;
        }
        if (!result.empty()) {
            result += " / ";
        }
        result += component;
    }
    return result.empty() ? "(empty)" : result;
}

void printUsage(const char* command) {
    std::cerr
        << "usage: " << command
        << " [MAPSET_FILE] [WORDBOOK_FILE]\n";
}

double elapsedMs(
    std::chrono::steady_clock::time_point start,
    std::chrono::steady_clock::time_point end) {
    return std::chrono::duration<double, std::milli>(end - start).count();
}

void reverseGeocode(
    const galuchat::GaluchatWGSMapSet3Reader& mapset,
    const galuchat::GaluchatGisWordBookReader& wordbook,
    double longitude,
    double latitude) {
    int64_t place_code = 0;
    auto reverse_start = std::chrono::steady_clock::now();
    bool found = mapset.readWgsPoint(longitude, latitude, place_code);
    auto reverse_end = std::chrono::steady_clock::now();

    std::cout << std::fixed << std::setprecision(6)
              << "coordinate: " << longitude << ", " << latitude << '\n';
    if (!found || place_code == 0) {
        std::cout << "not found\n"
                  << std::setprecision(3)
                  << "reversegeo: " << elapsedMs(reverse_start, reverse_end) << " ms\n";
        return;
    }

    std::vector<std::string> place_name;
    auto wordbook_start = std::chrono::steady_clock::now();
    bool name_found = wordbook.readStringSetByCode(place_code, place_name);
    auto wordbook_end = std::chrono::steady_clock::now();

    if (!name_found) {
        std::cout << "not found: place code has no name\n";
    } else {
        std::cout << "code: " << place_code << '\n'
                  << "place: " << joinPlaceName(place_name) << '\n';
    }
    std::cout << std::setprecision(3)
              << "reversegeo: " << elapsedMs(reverse_start, reverse_end) << " ms\n"
              << "wordbook: " << elapsedMs(wordbook_start, wordbook_end) << " ms\n";
}

} // namespace

int main(int argc, char** argv) {
    if (argc > 3) {
        printUsage(argv[0]);
        return 2;
    }

    try {
        std::string mapset_path = argc >= 2 ? argv[1] : DEFAULT_MAPSET;
        std::string wordbook_path = argc >= 3 ? argv[2] : DEFAULT_WORDBOOK;

        auto mapset_factory = std::make_shared<galuchat::FileReaderFactory>(
            mapset_path, FILE_BUFFER_SIZE);
        auto wordbook_factory = std::make_shared<galuchat::FileReaderFactory>(
            wordbook_path, FILE_BUFFER_SIZE);
        galuchat::GaluchatWGSMapSet3Reader mapset(mapset_factory);
        galuchat::GaluchatGisWordBookReader wordbook(wordbook_factory, 0);

        std::cout << "sample: Imperial Palace\n";
        reverseGeocode(mapset, wordbook, 139.7528, 35.6852);

        while (true) {
            double longitude;
            double latitude;
            std::printf("lon lat> ");
            std::fflush(stdout);
            int count = std::scanf("%lf %lf", &longitude, &latitude);
            if (count == EOF) break;
            if (count != 2) {
                std::cout << "enter longitude and latitude separated by a space\n";
                int c;
                while ((c = std::getchar()) != '\n' && c != EOF) {}
                continue;
            }
            reverseGeocode(mapset, wordbook, longitude, latitude);
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
