CXX ?= g++
CXXFLAGS ?= -O2 -Wall -Wextra -pedantic -std=c++17
CPPFLAGS ?= -I../../../src

TARGET := reverse-geocoding

.PHONY: all clean

all: $(TARGET)

$(TARGET): main.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $< -o $@

clean:
	$(RM) $(TARGET)
