#include <cstdint>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include "galuchat/wgsmap3_reader.hpp"

namespace {
using Bytes = std::vector<uint8_t>;

// Golden trace captured from SDK commit de0258a (before the chunk-index changes).
// Includes ReaderFactory calls, reads, skips, pos/atEnd queries, destruction,
// decoded results and errors. No indexed API is used by this test.
struct Trace {
    uint64_t hash = 14695981039346656037ull;
    uint64_t events = 0;
    size_t readers = 0;

    void mix(uint64_t value) {
        for (int i = 0; i < 8; ++i) {
            hash ^= value & 0xff;
            hash *= 1099511628211ull;
            value >>= 8;
        }
    }
    void event(char kind, uint64_t a = 0, uint64_t b = 0, uint64_t c = 0) {
        mix(static_cast<uint8_t>(kind)); mix(a); mix(b); mix(c);
        ++events;
    }
    void error(const std::string& message) {
        event('!');
        for (unsigned char byte : message) mix(byte);
    }
};

class Factory final : public galuchat::ReaderFactory {
public:
    Factory(const Bytes& bytes, Trace& trace) : bytes_(bytes), trace_(trace) {}
    std::unique_ptr<galuchat::ByteReader> create(size_t offset = 0) const override {
        size_t id = ++trace_.readers;
        trace_.event('C', id, offset);
        if (offset > bytes_.size()) throw std::runtime_error("invalid trace offset");
        class Reader final : public galuchat::ByteReader {
        public:
            Reader(const Bytes& bytes, Trace& trace, size_t id, size_t offset)
                : bytes_(bytes), trace_(trace), id_(id), offset_(offset) {}
            ~Reader() override { trace_.event('D', id_, pos_); }
            size_t pos() const override {
                trace_.event('P', id_, pos_);
                return pos_;
            }
            bool atEnd() const override {
                trace_.event('E', id_, pos_, pos_ == bytes_.size() - offset_);
                return pos_ == bytes_.size() - offset_;
            }
        protected:
            uint8_t nextByte() override {
                trace_.event('R', id_, pos_);
                if (pos_ >= bytes_.size() - offset_) throw std::runtime_error("trace EOF");
                return bytes_[offset_ + pos_++];
            }
            void skipByte(size_t length) override {
                trace_.event('S', id_, pos_, length);
                if (length > bytes_.size() - offset_ - pos_) throw std::runtime_error("trace EOF");
                pos_ += length;
            }
        private:
            const Bytes& bytes_;
            Trace& trace_;
            size_t id_, offset_, pos_ = 0;
        };
        return std::make_unique<Reader>(bytes_, trace_, id, offset);
    }
private:
    const Bytes& bytes_;
    Trace& trace_;
};

void append(Bytes& out, const Bytes& data) { out.insert(out.end(), data.begin(), data.end()); }
Bytes chunk(const char* tag, const Bytes& payload) {
    if (payload.size() >= 252) throw std::runtime_error("fixture too large");
    Bytes result(tag, tag + 4);
    result.push_back(static_cast<uint8_t>(payload.size()));
    append(result, payload);
    return result;
}

Bytes dataset(bool layout, bool bad_tail = false) {
    Bytes header(16, 0);
    std::string format = "WGSMapSet/3";
    for (size_t i = 0; i < format.size(); ++i) header[i] = format[i];
    append(header, {10,20,3,'x','y','z',3,10,20,11,21,30,40});
    Bytes out = chunk("GLCH", header);
    if (layout) append(out, chunk("LAYO", {1,2,3}));
    for (int map = 0; map < 3; ++map) {
        Bytes payload{4,4,1};
        for (int block = 0; block < 4; ++block) {
            uint8_t v = static_cast<uint8_t>(map * 4 + block + 1);
            append(payload, {0,0x70,v,v,v,v});
        }
        if (bad_tail && map == 0) payload.back() = 0xff; // Truncated MBUInt at end of a block.
        append(out, chunk("GI01", payload));
    }
    return out;
}

void rasterResult(Trace& trace, const galuchat::RawRaster& raster) {
    trace.event('V', raster.width, raster.height);
    for (int64_t value : raster.data) trace.mix(static_cast<uint64_t>(value));
}

template <class Call> void attempt(Trace& trace, Call call) {
    try { call(); } catch (const std::runtime_error& error) { trace.error(error.what()); }
}

void exercise(Trace& trace, const Bytes& bytes) {
    auto factory = std::make_shared<Factory>(bytes, trace);
    galuchat::GaluchatWGSMapSet3Reader reader(factory);
    auto area = reader.area();
    trace.event('A', area.x, area.y, reader.mapCount());
    trace.mix(area.width); trace.mix(area.height);
    trace.mix(reader.unit_inv_x); trace.mix(reader.unit_inv_y);
    for (unsigned char byte : reader.metadata) trace.mix(byte);
    for (const auto& rect : std::vector<galuchat::Rect>{
            {10,20,1,1}, {9,19,8,8}, {11,21,2,2}, {0,0,40,45},
            {0,0,1,1}, {10,20,0,0}, {13,23,3,3}, {30,40,1,1}}) {
        attempt(trace, [&] { rasterResult(trace, reader.readWgsRect(rect)); });
    }
    attempt(trace, [&] {
        galuchat::RawRaster pixel(1,1);
        reader.readWgsRect({10,20,2,1}, pixel);
    });
    attempt(trace, [&] { rasterResult(trace, reader.readWgsRect({10,20,-1,1})); });
    for (const auto& point : std::vector<galuchat::Rect>{
            {10,20,0,0}, {11,21,0,0}, {30,40,0,0}, {0,0,0,0}}) {
        attempt(trace, [&] {
            int64_t value = -1;
            bool found = reader.readWgsPoint(point.x, point.y, value);
            trace.event('F', found, static_cast<uint64_t>(value));
        });
    }
    attempt(trace, [&] {
        int64_t value = -1;
        bool found = reader.readWgsPoint(1.0, 1.0, value);
        trace.event('F', found, static_cast<uint64_t>(value));
    });
    attempt(trace, [&] { rasterResult(trace, reader.readRect(0,0,2,2)); });
    attempt(trace, [&] { rasterResult(trace, reader.readWgsRectf({1.0,1.0,0.2,0.1})); });
    attempt(trace, [&] { rasterResult(trace, reader.toRaster()); });
}
} // namespace

int main() {
    Trace trace;
    for (bool layout : {false,true}) for (bool bad_tail : {false,true}) {
        Bytes bytes = dataset(layout, bad_tail);
        exercise(trace, bytes);
    }
    Bytes bytes = dataset(false);
    bytes.push_back(0);
    attempt(trace, [&] { exercise(trace, bytes); });
    // Unchanged vector/pointer constructor signatures.
    bytes = dataset(true);
    galuchat::GaluchatWGSMapSet3Reader vector_reader(bytes);
    galuchat::GaluchatWGSMapSet3Reader pointer_reader(bytes.data(), bytes.size());
    rasterResult(trace, vector_reader.readWgsRect({10,20,1,1}));
    rasterResult(trace, pointer_reader.readWgsRect({30,40,1,1}));
    std::cout << "sequential trace: hash=" << trace.hash << " events=" << trace.events
              << " readers=" << trace.readers << '\n';
#ifndef GALUCHAT_CAPTURE_LEGACY_TRACE
    constexpr uint64_t ExpectedHash = 740967542500353378ull;
    constexpr uint64_t ExpectedEvents = 3410;
    constexpr size_t ExpectedReaders = 74;
    if (trace.hash != ExpectedHash || trace.events != ExpectedEvents || trace.readers != ExpectedReaders)
        throw std::runtime_error("sequential Reader I/O or output changed from de0258a");
#endif
}
