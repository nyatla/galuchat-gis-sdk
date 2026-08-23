#include <Arduino.h>
#include <cstdio>
#include <exception>
#include <string>
#include <vector>

#include "galuchat_bridge.hpp"

namespace {

namespace n03_data = galuchat::data::n03_20240101_100;

constexpr double LONGITUDE = 139.7528;
constexpr double LATITUDE = 35.6852;

void printElapsed(const char* label, uint32_t elapsed_us) {
    Serial.print(label);
    Serial.print(": ");
    Serial.print(static_cast<double>(elapsed_us) / 1000.0, 3);
    Serial.println(" ms");
}

void printPlaceName(const std::vector<std::string>& components) {
    bool first = true;
    for (const std::string& component : components) {
        if (component.empty()) {
            continue;
        }
        if (!first) {
            Serial.print(" / ");
        }
        Serial.print(component.c_str());
        first = false;
    }
    Serial.println();
}

void reverseGeocode(double longitude, double latitude) {
    // The byte arrays stay in Flash ROM. Readers only retain their addresses.
    static galuchat::GaluchatWGSMapSet3Reader mapset(
        n03_data::mapset, n03_data::mapset_size);
    static galuchat::GaluchatGisWordBookReader wordbook(
        n03_data::wordbook, n03_data::wordbook_size);
    static bool metadata_printed = false;
    if (!metadata_printed) {
        Serial.println("WGSMapSet metadata:");
        Serial.println(mapset.metadata.c_str());
        metadata_printed = true;
    }

    int64_t place_code = 0;
    uint32_t reverse_start = micros();
    bool found = mapset.readWgsPoint(longitude, latitude, place_code);
    uint32_t reverse_elapsed = micros() - reverse_start;

    Serial.print("coordinate: ");
    Serial.print(longitude, 6);
    Serial.print(", ");
    Serial.println(latitude, 6);
    if (!found || place_code == 0) {
        Serial.println("not found");
        printElapsed("reversegeo", reverse_elapsed);
        return;
    }

    std::vector<std::string> place_name;
    uint32_t wordbook_start = micros();
    bool name_found = wordbook.readStringSetByCode(place_code, place_name);
    uint32_t wordbook_elapsed = micros() - wordbook_start;
    if (!name_found) {
        Serial.println("not found");
    } else {
        Serial.print("code: ");
        Serial.println(static_cast<long>(place_code));
        Serial.print("place: ");
        printPlaceName(place_name);
    }
    printElapsed("reversegeo", reverse_elapsed);
    printElapsed("wordbook", wordbook_elapsed);
}

void printPrompt() {
    Serial.print("lon lat> ");
}

} // namespace

void setup() {
    Serial.begin(115200);
    delay(1000);

    try {
        Serial.println("sample: Imperial Palace");
        reverseGeocode(LONGITUDE, LATITUDE);
    } catch (const std::exception& error) {
        Serial.print("error: ");
        Serial.println(error.what());
    }
    printPrompt();
}

void loop() {
    if (!Serial.available()) return;
    String line = Serial.readStringUntil('\n');
    double longitude;
    double latitude;
    if (std::sscanf(line.c_str(), "%lf %lf", &longitude, &latitude) != 2) {
        Serial.println("enter longitude and latitude separated by a space");
        printPrompt();
        return;
    }
    try {
        reverseGeocode(longitude, latitude);
    } catch (const std::exception& error) {
        Serial.print("error: ");
        Serial.println(error.what());
    }
    printPrompt();
}
