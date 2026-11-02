#include <algorithm>
#include <climits>
#include <cstdint>
#include <functional>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

#include "galuchat/wgsmapset3_indexed_reader.hpp"

namespace {
using Bytes = std::vector<uint8_t>;

template <class T, class = void> struct HasWithoutTail : std::false_type {};
template <class T> struct HasWithoutTail<T, std::void_t<decltype(
    std::declval<const T&>().readWgsRectWithoutTail(std::declval<galuchat::Rect>()))>>
    : std::true_type {};
static_assert(!HasWithoutTail<galuchat::GaluchatWGSMapSet3Reader>::value,
              "indexed API leaked into the sequential reader");
static_assert(HasWithoutTail<galuchat::GaluchatWGSMapSet3IndexedReader>::value,
              "indexed reader lacks the no-tail API");
static_assert(!std::is_constructible<galuchat::GaluchatWGSMapSet3Reader,
              std::shared_ptr<const galuchat::ReaderFactory>, size_t>::value,
              "index options leaked into the sequential reader");

void require(bool condition, const char* label) {
    if (!condition) throw std::runtime_error(label);
}

void expectThrow(const std::function<void()>& call, const char* label) {
    try { call(); } catch (const std::runtime_error&) { return; }
    throw std::runtime_error(std::string("expected failure: ") + label);
}

void append(Bytes& out, const Bytes& bytes) {
    out.insert(out.end(), bytes.begin(), bytes.end());
}

Bytes chunk(const char* tag, const Bytes& payload) {
    require(payload.size() < 252, "fixture needs a larger MBUInt encoder");
    Bytes out(tag, tag + 4);
    out.push_back(static_cast<uint8_t>(payload.size()));
    append(out, payload);
    return out;
}

// One LZSS literal token, including the compressed stream's zero bit padding.
Bytes literals(const Bytes& decoded) {
    require(!decoded.empty() && decoded.size() <= 16, "literal fixture size");
    Bytes out;
    size_t bits = 0;
    auto write = [&](unsigned value, int count) {
        for (int i = count - 1; i >= 0; --i) {
            if (bits % 8 == 0) out.push_back(0);
            out.back() |= ((value >> i) & 1u) << (7 - bits % 8);
            ++bits;
        }
    };
    write(0, 1);
    write(static_cast<unsigned>(decoded.size() - 1), 4);
    for (uint8_t byte : decoded) write(byte, 8);
    return out;
}

Bytes block(int compression, const Bytes& decoded) {
    Bytes out{static_cast<uint8_t>(compression << 4)};
    if (compression == 0) append(out, decoded);
    else {
        Bytes payload = compression == 2 ? literals(decoded) : decoded;
        out.push_back(static_cast<uint8_t>(payload.size()));
        append(out, payload);
    }
    return out;
}

const std::vector<Bytes> BLOCKS{
    block(0, {0x43, 1, 2, 0x60}), // 1-bit RAW: 1,2 / 2,1; four padding bits.
    block(1, {0x70, 3, 4, 5, 6}), // RAWS
    block(2, {0x70, 7, 8, 9, 10}), // LZSS
    block(0, {0x70, 11, 12, 13, 14})
};

Bytes image(const std::vector<Bytes>& blocks = BLOCKS, int width = 4, int height = 4,
            const Bytes& extra = {}) {
    Bytes payload{static_cast<uint8_t>(width), static_cast<uint8_t>(height), 1};
    for (const auto& part : blocks) append(payload, part);
    append(payload, extra);
    return chunk("GI01", payload);
}

size_t blockEnd(int index) {
    size_t pos = 8; // GI01 tag + one-byte length + width/height/unit exponent.
    for (int i = 0; i <= index; ++i) pos += BLOCKS[i].size();
    return pos;
}

Bytes mapset(const std::vector<Bytes>& images, const std::vector<galuchat::Rect>& origins) {
    require(images.size() == origins.size(), "map fixture origins");
    Bytes header(16, 0);
    const std::string format = "WGSMapSet/3";
    std::copy(format.begin(), format.end(), header.begin());
    append(header, {1, 1, 0, static_cast<uint8_t>(images.size())});
    for (const auto& origin : origins) {
        require(origin.x >= 0 && origin.x < 124 && origin.y >= 0 && origin.y < 124,
                "map fixture coordinate");
        append(header, {static_cast<uint8_t>(origin.x), static_cast<uint8_t>(origin.y)});
    }
    Bytes out = chunk("GLCH", header);
    for (const auto& part : images) append(out, part);
    return out;
}

void checkRectangles() {
    // Also cover the existing low-level API's padded edge-block semantics.
    for (int dimension : {3, 4}) {
        Bytes bytes = image(BLOCKS, dimension, dimension);
        for (int x = -2; x <= 5; ++x) for (int y = -2; y <= 5; ++y)
        for (int w = 0; w <= 5; ++w) for (int h = 0; h <= 5; ++h) {
            galuchat::BufferReader full_source(bytes), partial_source(bytes);
            galuchat::GaluchatImageDataChunk01Reader full(full_source), partial(partial_source);
            galuchat::RawRaster expected(w, h), actual(w, h);
            std::fill(expected.data.begin(), expected.data.end(), -1);
            std::fill(actual.data.begin(), actual.data.end(), -1);
            full.readRect(x, y, expected);
            partial.readRectWithoutTail(x, y, actual);
            require(expected.data == actual.data, "GI01 rectangle pixels differ");
            require(full_source.pos() == bytes.size(), "legacy GI01 did not consume tail");
            size_t expected_pos = 8;
            // Independent oracle: which complete blocks contain requested pixels?
            for (int py = 0; py < h; ++py) for (int px = 0; px < w; ++px) {
                int sx = x + px, sy = y + py;
                if (sx >= 0 && sx < 4 && sy >= 0 && sy < 4)
                    expected_pos = std::max(expected_pos, blockEnd((sy / 2) * 2 + sx / 2));
            }
            require(partial_source.pos() == expected_pos, "partial GI01 read beyond last needed block");
            require(partial_source.bitOffset() == 0, "source not byte aligned");
        }
    }
    Bytes bytes = image();
    galuchat::BufferReader source(bytes);
    galuchat::GaluchatImageDataChunk01Reader reader(source);
    auto raster = reader.toRaster();
    const std::vector<int64_t> expected{1,2,3,4, 2,1,5,6, 7,8,11,12, 9,10,13,14};
    require(raster.data == expected, "fixture pixels do not match expected values");
}

void checkLifetimeAndStream() {
    Bytes first = image(), bytes = first;
    append(bytes, first);
    for (bool leave : {false, true}) {
        galuchat::BufferReader source(bytes);
        galuchat::GaluchatImageDataChunk01Reader reader(source);
        galuchat::RawRaster pixel(1, 1);
        if (leave) reader.readRectWithoutTail(0, 0, pixel);
        else reader.readRect(0, 0, pixel);
        require(pixel.get(0, 0) == 1, "stream pixel");
        expectThrow([&] { reader.readRect(0, 0, pixel); }, "reuse with legacy method");
        expectThrow([&] { reader.readRectWithoutTail(0, 0, pixel); }, "reuse with new method");
        if (leave) {
            require(source.pos() == blockEnd(0), "partial stream position");
            reader.skipToEnd();
        }
        require(source.pos() == first.size(), "next GI01 offset");
        galuchat::GaluchatImageDataChunk01Reader next(source);
        require(next.readPoint(2, 2) == 11, "next GI01 on shared stream");
        require(source.atEnd(), "shared stream not exhausted");
    }
    // Extreme coordinates must not overflow the last-block calculation.
    for (int coordinate : {INT_MIN, INT_MAX}) {
        galuchat::BufferReader source(first);
        galuchat::GaluchatImageDataChunk01Reader reader(source);
        galuchat::RawRaster pixel(1, 1);
        reader.readRectWithoutTail(coordinate, coordinate, pixel);
        require(source.pos() == 8, "outside rectangle consumed blocks");
    }
}

void checkValidation() {
    // Invalid unused tail: the old API still rejects it; the new API never touches it.
    auto blocks = BLOCKS;
    blocks.back() = {0x30}; // Reserved compression type.
    Bytes bytes = image(blocks);
    for (bool leave : {false, true}) {
        galuchat::BufferReader source(bytes);
        galuchat::GaluchatImageDataChunk01Reader reader(source);
        galuchat::RawRaster pixel(1, 1);
        if (leave) reader.readRectWithoutTail(0, 0, pixel);
        else expectThrow([&] { reader.readRect(0, 0, pixel); }, "invalid unused block");
        expectThrow([&] { reader.readRectWithoutTail(0, 0, pixel); }, "reader consumed after success/error");
    }
    // Unsized blocks in an unused tail still need structural parsing in legacy mode.
    blocks.back() = {0, 0xc0}; // Invalid CellHeader in an unsized RAW block.
    bytes = image(blocks);
    for (bool leave : {false, true}) {
        galuchat::BufferReader source(bytes);
        galuchat::GaluchatImageDataChunk01Reader reader(source);
        galuchat::RawRaster pixel(1, 1);
        if (leave) reader.readRectWithoutTail(0, 0, pixel);
        else expectThrow([&] { reader.readRect(0, 0, pixel); }, "unsized tail structure");
    }
    // A broken block before the requested area cannot be bypassed by the new API.
    auto broken_prefix = BLOCKS;
    broken_prefix.front() = {0x30};
    bytes = image(broken_prefix);
    {
        galuchat::BufferReader source(bytes);
        galuchat::GaluchatImageDataChunk01Reader reader(source);
        galuchat::RawRaster pixel(1, 1);
        expectThrow([&] { reader.readRectWithoutTail(2, 0, pixel); }, "invalid prefix block");
    }
    // Only the existing API enforces exact GI01 payload length, even for the full rectangle.
    bytes = image(BLOCKS, 4, 4, {0});
    for (bool leave : {false, true}) {
        galuchat::BufferReader source(bytes);
        galuchat::GaluchatImageDataChunk01Reader reader(source);
        galuchat::RawRaster raster(4, 4);
        if (leave) reader.readRectWithoutTail(0, 0, raster);
        else expectThrow([&] { reader.readRect(0, 0, raster); }, "GI01 length mismatch");
    }
    // Per-block validation remains mandatory, including at the final needed block.
    std::vector<Bytes> bad_blocks{
        {0x30},                    // Reserved block header.
        block(1, {0x70, 1, 2, 3, 4, 0}), // RAWS trailing byte.
        {0x10, 1, 0x70},           // RAWS truncated values.
        block(2, {0x70, 1, 2, 3, 4, 0}), // Extra decoded LZSS byte.
        {0x20, 1, 0},              // Truncated LZSS token.
        {0, 0x70, 1}               // Truncated unsized RAW block.
    };
    Bytes bad_padding = block(2, {0x70, 1, 2, 3, 4});
    bad_padding.back() |= 1;
    bad_blocks.push_back(bad_padding);
    for (const auto& bad : bad_blocks) for (bool leave : {false, true}) {
        bytes = image({bad}, 2, 2);
        galuchat::BufferReader source(bytes);
        galuchat::GaluchatImageDataChunk01Reader reader(source);
        galuchat::RawRaster pixel(1, 1);
        expectThrow([&] {
            if (leave) reader.readRectWithoutTail(0, 0, pixel);
            else reader.readRect(0, 0, pixel);
        }, "invalid selected block");
    }
    // Needed blocks are validated even if preceded by skipped blocks.
    bytes = image(blocks);
    galuchat::BufferReader source(bytes);
    galuchat::GaluchatImageDataChunk01Reader reader(source);
    galuchat::RawRaster pixel(1, 1);
    expectThrow([&] { reader.readRectWithoutTail(2, 2, pixel); }, "invalid final selected block");
}

struct Access {
    size_t offset;
    size_t end = 0;
};

// Records logical reads AND skips; seeking over a tail would also fail the test.
class TracedFactory final : public galuchat::ReaderFactory {
public:
    explicit TracedFactory(const Bytes& bytes) : bytes_(bytes) {}
    std::unique_ptr<galuchat::ByteReader> create(size_t offset = 0) const override {
        require(offset <= bytes_.size(), "factory offset");
        auto access = std::make_shared<Access>();
        access->offset = offset;
        accesses.push_back(access);
        class Reader final : public galuchat::ByteReader {
        public:
            Reader(const Bytes& bytes, std::shared_ptr<Access> access)
                : bytes_(bytes), access_(std::move(access)) {}
            size_t pos() const override { return access_->end; }
            bool atEnd() const override { return pos() == bytes_.size() - access_->offset; }
        protected:
            uint8_t nextByte() override {
                require(!atEnd(), "unexpected traced EOF");
                return bytes_[access_->offset + access_->end++];
            }
        private:
            const Bytes& bytes_;
            std::shared_ptr<Access> access_;
        };
        return std::make_unique<Reader>(bytes_, access);
    }
    mutable std::vector<std::shared_ptr<Access>> accesses;
private:
    const Bytes& bytes_;
};

void checkMapSet() {
    Bytes overlay = image({block(0, {0x70, 0, 90, 0, 91})}, 2, 2);
    Bytes bytes = mapset({image(), overlay, image()}, {{10,20,0,0}, {11,21,0,0}, {30,40,0,0}});
    auto factory = std::make_shared<TracedFactory>(bytes);
    galuchat::GaluchatWGSMapSet3Reader sequential(bytes);
    galuchat::GaluchatWGSMapSet3IndexedReader reader(factory);
    // Empty, outside, clipped, overlapping and multiple independently opened GI01s.
    for (const auto& rect : std::vector<galuchat::Rect>{
            {10,20,1,1}, {9,19,5,5}, {11,21,2,2}, {0,0,40,45},
            {0,0,1,1}, {10,20,0,0}, {13,23,3,3}, {30,40,1,1}}) {
        auto expected = sequential.readWgsRect(rect);
        require(expected.data == reader.readWgsRect(rect).data, "indexed full-tail pixels differ");
        auto actual = reader.readWgsRectWithoutTail(rect);
        require(expected.data == actual.data, "mapset pixels differ");
        galuchat::RawRaster provided(rect.width, rect.height);
        std::fill(provided.data.begin(), provided.data.end(), -1);
        reader.readWgsRectWithoutTail(rect, provided);
        require(expected.data == provided.data, "destination overload / zero fill");
    }
    auto composite = reader.readWgsRectWithoutTail({11,21,2,2});
    require(composite.data == std::vector<int64_t>({1,90,8,91}), "overlay / zero transparency");
    factory->accesses.clear();
    reader.readWgsRectWithoutTail({10,20,1,1});
    require(factory->accesses.size() == 1, "nonintersecting map opened");
    require(factory->accesses[0]->end == blockEnd(0), "mapset traversed unused tail");
    factory->accesses.clear();
    reader.readWgsRect({10,20,1,1});
    require(factory->accesses.size() == 1 && factory->accesses[0]->end == image().size(),
            "indexed full-tail API did not consume all blocks");
    galuchat::RawRaster pixel(1, 1);
    expectThrow([&] { reader.readWgsRectWithoutTail({10,20,2,1}, pixel); }, "target mismatch");
    expectThrow([&] { reader.readWgsRectWithoutTail({10,20,-1,1}); }, "negative dimensions");
    int64_t point = 0;
    require(reader.readWgsPoint(30, 40, point) && point == 1, "legacy point stream changed");

    auto bad = BLOCKS;
    bad.back() = {0x30};
    bytes = mapset({image(bad)}, {{10,20,0,0}});
    galuchat::GaluchatWGSMapSet3Reader corrupt_sequential(bytes);
    galuchat::GaluchatWGSMapSet3IndexedReader corrupt(bytes);
    expectThrow([&] { corrupt_sequential.readWgsRect({10,20,1,1}); }, "sequential tail validation");
    expectThrow([&] { corrupt.readWgsRect({10,20,1,1}); }, "indexed full-tail validation");
    require(corrupt.readWgsRectWithoutTail({10,20,1,1}).get(0,0) == 1,
            "new mapset touched invalid unused tail");
}

void checkIndexedLimits() {
    Bytes bytes = mapset({image(), image()}, {{10,20,0,0}, {30,40,0,0}});
    auto factory = std::make_shared<TracedFactory>(bytes);
    for (size_t limit : {size_t{0}, size_t{1}}) {
        factory->accesses.clear();
        bool rejected = false;
        try {
            galuchat::GaluchatWGSMapSet3IndexedReader reader(factory, limit);
        } catch (const galuchat::MapCountLimitExceeded& error) {
            require(error.count == 2 && error.limit == limit, "incorrect limit error details");
            rejected = true;
        }
        require(rejected, "oversized mapset accepted");
        require(factory->accesses.size() == 1 && factory->accesses[0]->end == 25,
                "limit rejected after scanning origins/chunks");
    }
    galuchat::GaluchatWGSMapSet3IndexedReader vector_reader(bytes, 2);
    galuchat::GaluchatWGSMapSet3IndexedReader pointer_reader(bytes.data(), bytes.size(), 2);
    galuchat::GaluchatWGSMapSet3IndexedReader factory_reader(factory, 2);
    require(vector_reader.mapCount() == 2 && pointer_reader.mapCount() == 2
            && factory_reader.mapCount() == 2, "inclusive map limit / constructors");
    require(vector_reader.readWgsRectWithoutTail({30,40,1,1}).get(0,0) == 1,
            "vector indexed constructor result");
    require(pointer_reader.readWgsRectWithoutTail({30,40,1,1}).get(0,0) == 1,
            "pointer indexed constructor result");
    auto expected = vector_reader.readWgsRect({10,20,1,1});
    require(expected.data == vector_reader.readRect(0,0,1,1).data,
            "indexed local rectangle wrapper");
    require(expected.data == vector_reader.readWgsRectf({10.0,20.0,1.0,1.0}).data,
            "indexed floating rectangle wrapper");
    require(vector_reader.toRaster().get(0,0) == 1, "indexed full raster wrapper");
    galuchat::GaluchatWGSMapSet3Reader sequential(bytes);
    require(sequential.mapCount() == 2, "sequential reader acquired a map limit");
}
} // namespace

int main() {
    checkRectangles();
    checkLifetimeAndStream();
    checkValidation();
    checkMapSet();
    checkIndexedLimits();
    std::cout << "rectangle APIs: compatibility, early stop, streams, validation and composition OK\n";
}
