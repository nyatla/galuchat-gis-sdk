ARDUINO_CLI ?= arduino-cli
ARDUINO_CLI_FLAGS ?=
FQBN ?= esp32:esp32:esp32
BUILD_ROOT ?= $(CURDIR)/build

.PHONY: all reverse-geocoding reverse-geocoding-file clean

all: reverse-geocoding reverse-geocoding-file

reverse-geocoding:
	$(ARDUINO_CLI) $(ARDUINO_CLI_FLAGS) compile --fqbn $(FQBN) \
		--build-path $(BUILD_ROOT)/reverse-geocoding reverse-geocoding

reverse-geocoding-file:
	$(ARDUINO_CLI) $(ARDUINO_CLI_FLAGS) compile --fqbn $(FQBN) \
		--build-path $(BUILD_ROOT)/reverse-geocoding-file reverse-geocoding-file

clean:
	$(RM) -r $(BUILD_ROOT)
