#pragma once

#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

namespace galuchat {

namespace detail {

inline size_t toSize(uint64_t value, const char* field) {
    if (value > std::numeric_limits<size_t>::max()) {
        throw std::runtime_error(std::string(field) + " is out of range");
    }
    return static_cast<size_t>(value);
}

inline int toInt(uint64_t value, const char* field) {
    if (value > static_cast<uint64_t>(std::numeric_limits<int>::max())) {
        throw std::runtime_error(std::string(field) + " is out of range");
    }
    return static_cast<int>(value);
}

inline int toInt(int64_t value, const char* field) {
    if (value < std::numeric_limits<int>::min()
        || value > std::numeric_limits<int>::max()) {
        throw std::runtime_error(std::string(field) + " is out of range");
    }
    return static_cast<int>(value);
}

inline int positiveInt(uint64_t value, const char* field) {
    int result = toInt(value, field);
    if (result <= 0) {
        throw std::runtime_error(std::string(field) + " must be positive");
    }
    return result;
}

inline int addInt(int left, int right, const char* field) {
    return toInt(static_cast<int64_t>(left) + right, field);
}

inline int subtractInt(int left, int right, const char* field) {
    return toInt(static_cast<int64_t>(left) - right, field);
}

inline int multiplyInt(int left, int right, const char* field) {
    return toInt(static_cast<int64_t>(left) * right, field);
}

inline size_t addSize(size_t left, size_t right, const char* field) {
    if (right > std::numeric_limits<size_t>::max() - left) {
        throw std::runtime_error(std::string(field) + " is out of range");
    }
    return left + right;
}

inline size_t multiplySize(size_t left, size_t right, const char* field) {
    if (right != 0 && left > std::numeric_limits<size_t>::max() / right) {
        throw std::runtime_error(std::string(field) + " is out of range");
    }
    return left * right;
}

inline int roundedInt(double value, const char* field) {
    if (!std::isfinite(value)
        || value <= static_cast<double>(std::numeric_limits<int>::min()) - 0.5
        || value >= static_cast<double>(std::numeric_limits<int>::max()) + 0.5) {
        throw std::runtime_error(std::string(field) + " is out of range");
    }
    return static_cast<int>(std::llround(value));
}

} // namespace detail

class ByteReader {
public:
    virtual ~ByteReader() = default;

    virtual size_t pos() const = 0;
    virtual bool atEnd() const = 0;
    int bitOffset() const { return bit_left_; }

    uint32_t readBitsAsInt32(int bits) {
        if (bits < 0 || bits > 31) {
            throw std::runtime_error("bits must be in 0..31");
        }
        if (bits == 0) {
            return 0;
        }
        uint32_t result = 0;
        int left = bit_left_;
        uint32_t cache = bit_cache_;
        int remaining = bits;
        if (left > 0) {
            int read_bits = left < remaining ? left : remaining;
            result = (cache >> (left - read_bits)) & ((1u << read_bits) - 1u);
            left -= read_bits;
            remaining -= read_bits;
            cache = left > 0 ? cache & ((1u << left) - 1u) : 0;
        }
        while (remaining >= 8) {
            result = (result << 8) | nextByte();
            remaining -= 8;
        }
        if (remaining > 0) {
            uint32_t next = nextByte();
            result = (result << remaining) | (next >> (8 - remaining));
            left = 8 - remaining;
            cache = next & ((1u << left) - 1u);
        }
        bit_left_ = left;
        bit_cache_ = cache;
        return result;
    }

    uint8_t readByte() {
        int left = bit_left_;
        uint32_t next = nextByte();
        if (left == 0) {
            return static_cast<uint8_t>(next);
        }
        uint32_t merged = (bit_cache_ << 8) | next;
        uint8_t result = static_cast<uint8_t>((merged >> left) & 0xff);
        bit_cache_ = merged & ((1u << left) - 1u);
        return result;
    }

    void skipToByte() {
        bit_left_ = 0;
        bit_cache_ = 0;
    }

    void skipBits(size_t bits) {
        if (bit_left_ > 0) {
            size_t consumed = bits < static_cast<size_t>(bit_left_)
                ? bits : static_cast<size_t>(bit_left_);
            bit_left_ -= static_cast<int>(consumed);
            bits -= consumed;
            bit_cache_ = bit_left_ > 0
                ? bit_cache_ & ((1u << bit_left_) - 1u)
                : 0;
            if (bits == 0) return;
        }
        size_t bytes = bits / 8;
        if (bytes > 0) {
            skipByte(bytes);
            bits -= bytes * 8;
        }
        if (bits > 0) {
            uint32_t next = nextByte();
            bit_left_ = 8 - static_cast<int>(bits);
            bit_cache_ = next & ((1u << bit_left_) - 1u);
        }
    }

    void skipInByte(size_t length) {
        if (length == 0) {
            return;
        }
        if (bit_left_ == 0) {
            skipByte(length);
            return;
        }
        if (length > 1) {
            skipByte(length - 1);
        }
        readByte();
    }

    uint64_t readMbUInt() {
        uint8_t prefix = readByte();
        if (prefix < 252) {
            return prefix;
        }
        if (prefix == 255) {
            return 252ull + readByte();
        }
        if (prefix == 254) {
            return 508ull + (static_cast<uint64_t>(readByte()) << 8) + readByte();
        }
        if (prefix == 253) {
            return 66044ull
                + (static_cast<uint64_t>(readByte()) << 16)
                + (static_cast<uint64_t>(readByte()) << 8)
                + readByte();
        }
        if (prefix == 252) {
            return 16843260ull
                + (static_cast<uint64_t>(readByte()) << 24)
                + (static_cast<uint64_t>(readByte()) << 16)
                + (static_cast<uint64_t>(readByte()) << 8)
                + readByte();
        }
        throw std::runtime_error("invalid MBUInt prefix");
    }

    int64_t readMbInt() {
        uint8_t head = readByte();
        int64_t sign = (head & 0x80) != 0 ? -1 : 1;
        uint8_t prefix = head & 0x7f;
        if (prefix < 124) {
            return sign * prefix;
        }
        if (prefix == 127) {
            return sign * (124ll + readByte());
        }
        if (prefix == 126) {
            return sign * (380ll + (static_cast<int64_t>(readByte()) << 8) + readByte());
        }
        if (prefix == 125) {
            return sign * (65916ll
                + (static_cast<int64_t>(readByte()) << 16)
                + (static_cast<int64_t>(readByte()) << 8)
                + readByte());
        }
        if (prefix == 124) {
            return sign * (16843132ll
                + (static_cast<int64_t>(readByte()) << 24)
                + (static_cast<int64_t>(readByte()) << 16)
                + (static_cast<int64_t>(readByte()) << 8)
                + readByte());
        }
        throw std::runtime_error("invalid MBInt prefix");
    }

protected:
    virtual uint8_t nextByte() = 0;
    virtual void skipByte(size_t length) {
        for (size_t i = 0; i < length; i++) {
            nextByte();
        }
    }

private:
    int bit_left_ = 0;
    uint32_t bit_cache_ = 0;
};

class BufferReader final : public ByteReader {
public:
    BufferReader(const uint8_t* data, size_t size) : data_(data), size_(size) {}
    BufferReader(const std::vector<uint8_t>& data) : data_(data.data()), size_(data.size()) {}

    size_t pos() const override { return pos_; }
    bool atEnd() const override { return pos_ == size_; }
    size_t remaining() const { return size_ - pos_; }

protected:
    uint8_t nextByte() override {
        if (pos_ >= size_) {
            throw std::runtime_error("unexpected end of byte stream");
        }
        return data_[pos_++];
    }

    void skipByte(size_t length) override {
        if (length > remaining()) {
            throw std::runtime_error("unexpected end of byte stream");
        }
        pos_ += length;
    }

private:
    const uint8_t* data_;
    size_t size_;
    size_t pos_ = 0;
};

/** Restricts reads from another reader to one declared byte range. */
namespace detail {

inline std::string readAscii(ByteReader& reader, size_t length) {
    std::string result(length, '\0');
    for (size_t i = 0; i < length; i++) {
        result[i] = static_cast<char>(reader.readByte());
    }
    return result;
}

inline std::string readBStrAscii(ByteReader& reader, size_t length) {
    std::string result = readAscii(reader, length);
    size_t zero = result.find('\0');
    if (zero != std::string::npos) result.resize(zero);
    return result;
}

class LimitedReader final : public ByteReader {
public:
    LimitedReader(ByteReader& source, size_t length)
        : source_(source), length_(length) {}

    size_t pos() const override { return pos_; }
    bool atEnd() const override { return pos_ == length_; }
    size_t remaining() const { return length_ - pos_; }

protected:
    uint8_t nextByte() override {
        if (atEnd()) throw std::runtime_error("declared byte range exceeded");
        uint8_t value = source_.readByte();
        pos_++;
        return value;
    }

    void skipByte(size_t length) override {
        if (length > remaining()) {
            throw std::runtime_error("declared byte range exceeded");
        }
        source_.skipInByte(length);
        pos_ += length;
    }

private:
    ByteReader& source_;
    size_t length_;
    size_t pos_ = 0;
};

} // namespace detail

class ReaderFactory {
public:
    virtual ~ReaderFactory() = default;
    virtual std::unique_ptr<ByteReader> create(size_t offset = 0) const = 0;
};

class BufferReaderFactory final : public ReaderFactory {
public:
    BufferReaderFactory(const uint8_t* data, size_t size) : data_(data), size_(size) {}
    explicit BufferReaderFactory(const std::vector<uint8_t>& data)
        : data_(data.data()), size_(data.size()) {}

    std::unique_ptr<ByteReader> create(size_t offset = 0) const override {
        if (offset > size_) throw std::runtime_error("invalid reader offset");
        return std::make_unique<BufferReader>(data_ + offset, size_ - offset);
    }

private:
    const uint8_t* data_;
    size_t size_;
};

namespace detail {

class LzssReader final : public ByteReader {
public:
    explicit LzssReader(LimitedReader& source) : source_(source) {
        window_.fill(0);
    }

    size_t pos() const override { return output_pos_; }
    bool atEnd() const override { return finished_ && state_ == 0; }

    void validateEnd() {
        if (bitOffset() != 0) {
            throw std::runtime_error("decoded LZSS reader is not byte aligned");
        }
        try {
            (void)nextByte();
        } catch (const CleanEnd&) {
            return;
        }
        throw std::runtime_error("GI01 block payload has trailing bytes");
    }

protected:
    uint8_t nextByte() override {
        while (true) {
            if (state_ == 0) {
                startToken();
            }
            if (state_ == 10) {
                limit_ = static_cast<int>(source_.readBitsAsInt32(4)) + 1;
                index_ = 0;
                state_ = 11;
            }
            if (state_ == 11) {
                uint8_t value = source_.readByte();
                push(value);
                if (++index_ >= limit_) {
                    state_ = 0;
                }
                output_pos_++;
                return value;
            }
            if (state_ == 20) {
                ref_offset_ = source_.readByte();
                index_ = 0;
                limit_ = static_cast<int>(source_.readBitsAsInt32(4)) + 2;
                state_ = 21;
            }
            if (state_ == 21) {
                uint8_t value = get(ref_offset_);
                push(value);
                if (++index_ >= limit_) {
                    state_ = 0;
                }
                output_pos_++;
                return value;
            }
        }
    }

private:
    class CleanEnd final : public std::exception {};

    void startToken() {
        if (finished_) throw CleanEnd();
        size_t remaining_bits = detail::multiplySize(
            source_.remaining(), size_t{8}, "LZSS remaining bits")
            + static_cast<size_t>(source_.bitOffset());
        if (remaining_bits <= 7) {
            if (remaining_bits > 0
                && source_.readBitsAsInt32(static_cast<int>(remaining_bits)) != 0) {
                throw std::runtime_error("invalid non-zero LZSS padding");
            }
            finished_ = true;
            throw CleanEnd();
        }
        state_ = source_.readBitsAsInt32(1) == 0 ? 10 : 20;
    }

    uint8_t get(int index) const {
        return window_[(ptr_ + index) & 0xff];
    }
    void push(uint8_t value) {
        window_[ptr_] = value;
        ptr_ = (ptr_ + 1) & 0xff;
    }

    LimitedReader& source_;
    std::array<uint8_t, 256> window_{};
    int ptr_ = 0;
    int state_ = 0;
    int limit_ = 0;
    int index_ = 0;
    int ref_offset_ = 0;
    size_t output_pos_ = 0;
    bool finished_ = false;
};

} // namespace detail

struct RawRaster {
    int width = 0;
    int height = 0;
    std::vector<int64_t> data;

    RawRaster() = default;
    RawRaster(int w, int h) : width(w), height(h), data(pixelCount(w, h)) {}

    int64_t get(int x, int y) const {
        return data[static_cast<size_t>(y) * width + x];
    }
    void set(int x, int y, int64_t value) {
        data[static_cast<size_t>(y) * width + x] = value;
    }

private:
    static size_t pixelCount(int width, int height) {
        if (width < 0 || height < 0) {
            throw std::runtime_error("raster size must not be negative");
        }
        size_t w = static_cast<size_t>(width);
        size_t h = static_cast<size_t>(height);
        if (h != 0 && w > std::numeric_limits<size_t>::max() / h) {
            throw std::runtime_error("raster size is out of range");
        }
        size_t count = w * h;
        if (count > std::vector<int64_t>().max_size()) {
            throw std::runtime_error("raster size is out of range");
        }
        return count;
    }
};

template <class Value>
struct RasterView {
    int width;
    int height;
    Value* data;
    size_t stride;

    RasterView(int w, int h, Value* values, size_t row_stride = 0)
        : width(w), height(h), data(values), stride(row_stride == 0 ? static_cast<size_t>(w) : row_stride) {
        if (w < 0 || h < 0 || (w > 0 && h > 0 && values == nullptr)
            || stride < static_cast<size_t>(w)) {
            throw std::runtime_error("invalid raster view");
        }
    }

    void set(int x, int y, int64_t value) {
        data[static_cast<size_t>(y) * stride + x] = static_cast<Value>(value);
    }
};

struct Rect {
    int x;
    int y;
    int width;
    int height;
};

struct DoubleRect {
    double x;
    double y;
    double width;
    double height;
};

namespace detail {

inline bool insideRect(const Rect& r, int x, int y) {
    if (r.width < 0 || r.height < 0) return false;
    int64_t right = static_cast<int64_t>(r.x) + r.width;
    int64_t bottom = static_cast<int64_t>(r.y) + r.height;
    return r.x <= x && static_cast<int64_t>(x) < right
        && r.y <= y && static_cast<int64_t>(y) < bottom;
}

inline bool crossRect(const Rect& a, const Rect& b, Rect& out) {
    if (a.width < 0 || a.height < 0 || b.width < 0 || b.height < 0) {
        throw std::runtime_error("rectangle size must not be negative");
    }
    int x = a.x > b.x ? a.x : b.x;
    int y = a.y > b.y ? a.y : b.y;
    int64_t a_right = static_cast<int64_t>(a.x) + a.width;
    int64_t b_right = static_cast<int64_t>(b.x) + b.width;
    int64_t a_bottom = static_cast<int64_t>(a.y) + a.height;
    int64_t b_bottom = static_cast<int64_t>(b.y) + b.height;
    int64_t right = a_right < b_right ? a_right : b_right;
    int64_t bottom = a_bottom < b_bottom ? a_bottom : b_bottom;
    if (static_cast<int64_t>(x) >= right || static_cast<int64_t>(y) >= bottom) {
        return false;
    }
    out = {
        x,
        y,
        detail::toInt(right - x, "rectangle width"),
        detail::toInt(bottom - y, "rectangle height"),
    };
    return true;
}

template <class Raster>
inline void fillRect(Raster& dest, int x, int y, int width, int height, int64_t value) {
    for (int iy = 0; iy < height; iy++) {
        for (int ix = 0; ix < width; ix++) {
            dest.set(x + ix, y + iy, value);
        }
    }
}

struct CellHeader {
    static constexpr int CONTAINER_TYPE_MIXED = 0;
    static constexpr int CONTAINER_TYPE_VALUES = 1;
    static constexpr int CONTAINER_TYPE_MONO = 2;
    static constexpr int CONTAINER_TYPE_RESERVED = 3;

    static constexpr int PALLET_1BIT = 0;
    static constexpr int PALLET_2BIT = 1;
    static constexpr int PALLET_4BIT = 2;
    static constexpr int PALLET_NBIT = 3;

    static constexpr int RLE_PALLET_2 = 0;
    static constexpr int RLE_PALLET_3 = 1;
    static constexpr int RLE_PALLET_5 = 2;
    static constexpr int RLE_PALLET_16 = 3;

    static constexpr int RLE_DATA_ENCODING_MBUINT = 0;
    static constexpr int RLE_DATA_ENCODING_SHORT_VALUE = 1;
    static constexpr int RLE_DATA_ENCODING_SINGLE_EDGE_ROW = 2;

    explicit CellHeader(uint8_t b) : byte1(b) {}
    uint8_t byte1;

    bool isNode() const { return ((byte1 >> 6) & 0x03) == 0; }
    bool isRaw() const { return ((byte1 >> 6) & 0x03) == 1; }
    bool isRle() const { return ((byte1 >> 6) & 0x03) == 2; }
    int palletResolution() const { return (byte1 >> 4) & 0x03; }
    int rawUpdatePalletTableLow4() const { return byte1 & 0x0f; }
    int rleMode() const { return byte1 & 0x03; }
    int rleDataEncoding() const { return (byte1 >> 2) & 0x03; }
    int containerType() const { return (byte1 >> 4) & 0x03; }
    int updatePalletTable4() const { return byte1 & 0x0f; }

    int numOfPallet() const {
        if (isRle()) {
            static constexpr int values[] = {2, 3, 5, 16};
            return values[palletResolution()];
        }
        if (isRaw()) {
            static constexpr int values[] = {2, 4, 16, 0};
            return values[palletResolution()];
        }
        return 0;
    }

    bool hasValidRawReservedBits() const {
        if (palletResolution() == PALLET_NBIT) {
            return rawUpdatePalletTableLow4() == 0;
        }
        if (palletResolution() == PALLET_1BIT) {
            return rawUpdatePalletTableLow4() < 0x04;
        }
        return true;
    }

    bool hasValidRleReservedBits() const {
        int encoding = rleDataEncoding();
        return encoding == RLE_DATA_ENCODING_MBUINT
            || encoding == RLE_DATA_ENCODING_SHORT_VALUE
            || encoding == RLE_DATA_ENCODING_SINGLE_EDGE_ROW;
    }

    bool hasValidContainerHeader() const {
        int type = containerType();
        int update = updatePalletTable4();
        return type != CONTAINER_TYPE_RESERVED
            && (type != CONTAINER_TYPE_MIXED || (update & 0x01) == 0)
            && (type != CONTAINER_TYPE_MONO || (update & 0x07) == 0);
    }
};

struct PalletMgr {
    std::array<int64_t, 16> table{};
    int64_t getValue(int index) const { return table[static_cast<size_t>(index)]; }
};

struct PalletValueReader {
    bool delta;
    explicit PalletValueReader(bool d) : delta(d) {}

    void applyTable(ByteReader& reader, PalletMgr& pmgr, int update_table, int width) const {
        for (int slot = 0; slot < width; slot++) {
            int bit = 1 << (width - 1 - slot);
            if ((update_table & bit) == 0) {
                continue;
            }
            pmgr.table[slot] = delta ? pmgr.table[slot] + reader.readMbInt()
                                     : static_cast<int64_t>(reader.readMbUInt());
        }
    }
};

struct PalletHeader {
    int pallet_mode;
    int capacity;
    int update_pallet_table;
    int initial_index;
    bool has_initial_index;
    int value_bits_add;

    static PalletHeader readFrom(ByteReader& reader, int pallet_mode) {
        if (pallet_mode == CellHeader::RLE_PALLET_2) {
            int bits = static_cast<int>(reader.readBitsAsInt32(7));
            return {pallet_mode, 2, (bits >> 4) & 0x03, bits >> 6, true, bits & 0x0f};
        }
        if (pallet_mode == CellHeader::RLE_PALLET_3) {
            int bits = static_cast<int>(reader.readBitsAsInt32(9));
            return {pallet_mode, 3, (bits >> 4) & 0x07, bits >> 7, true, bits & 0x0f};
        }
        if (pallet_mode == CellHeader::RLE_PALLET_5) {
            int bits = static_cast<int>(reader.readBitsAsInt32(12));
            return {pallet_mode, 5, (bits >> 4) & 0x1f, bits >> 9, true, bits & 0x0f};
        }
        if (pallet_mode == CellHeader::RLE_PALLET_16) {
            int bits = static_cast<int>(reader.readBitsAsInt32(20));
            return {pallet_mode, 16, bits >> 4, 0, false, bits & 0x0f};
        }
        throw std::runtime_error("invalid RLE pallet mode");
    }
};

struct NodePallet {
    int mask;
    int container_type;
    std::array<int64_t, 4> pallet;

    bool palletValue(int child_index, int64_t& value) const {
        int index = (mask >> ((3 - child_index) * 2)) & 0x03;
        if (container_type == CellHeader::CONTAINER_TYPE_MIXED && index == 3) {
            return false;
        }
        value = pallet[static_cast<size_t>(index)];
        return true;
    }
};

inline int mapIndex(int resolution, int mode, int index) {
    auto zigzag = [](int size, int i) {
        int y = i / size;
        int x = i % size;
        return (y & 1) == 0 ? x + y * size : (size - 1) + y * size - x;
    };
    auto mirror_x = [](int size, int i) {
        int x = i % size;
        int y = i / size;
        return (size - 1 - x) + y * size;
    };
    auto mirror_y = [](int size, int i) {
        int x = i % size;
        int y = i / size;
        return x + (size - 1 - y) * size;
    };
    auto transpose = [](int size, int i) {
        int x = i / size;
        int y = i % size;
        return x + y * size;
    };
    switch (mode) {
    case 0:
        return zigzag(resolution, index);
    case 1:
        return zigzag(resolution, mirror_x(resolution, index));
    case 2:
        return transpose(resolution, zigzag(resolution, index));
    case 3:
        return transpose(resolution, zigzag(resolution, mirror_y(resolution, index)));
    default:
        throw std::runtime_error("invalid RLE scan mode");
    }
}

class ShortValueRleLenDecoder {
public:
    ShortValueRleLenDecoder(int resolution, int value_bits_add, int run_bits_add) {
        struct P { int res; int run_bits; int run_min; int base_value_bits; };
        static constexpr P params[] = {
            {8, 3, 2, 2}, {16, 3, 2, 2}, {32, 4, 4, 3},
            {64, 4, 4, 4}, {128, 4, 4, 4}, {256, 5, 4, 4},
        };
        if (value_bits_add < 0 || value_bits_add > 3
            || run_bits_add < 0 || run_bits_add > 1) {
            throw std::runtime_error("invalid ShortValue encoding parameters");
        }
        for (const auto& p : params) {
            if (p.res == resolution) {
                supported_ = true;
                run_bits_ = p.run_bits + run_bits_add;
                run_min_ = p.run_min;
                run_max_ = p.run_min + (1 << run_bits_) - 1;
                value_bits_ = p.base_value_bits + value_bits_add;
                return;
            }
        }
    }

    int readToken(ByteReader& reader, int* dest, int limit) const {
        int prefix = static_cast<int>(reader.readBitsAsInt32(1));
        if (prefix == 0) {
            if (limit < 1) {
                throw std::runtime_error("MBUInt token exceeds requested count");
            }
            dest[0] = detail::toInt(reader.readMbUInt(), "ShortValue MBUInt token");
            return 1;
        }
        if (!supported_) {
            throw std::runtime_error("unsupported ShortValue resolution");
        }
        int run = static_cast<int>(reader.readBitsAsInt32(run_bits_)) + run_min_;
        if (run > run_max_ || run > limit) {
            throw std::runtime_error("invalid ShortValue run length");
        }
        for (int i = 0; i < run; i++) {
            dest[i] = static_cast<int>(reader.readBitsAsInt32(value_bits_)) + 1;
        }
        return run;
    }

private:
    bool supported_ = false;
    int run_bits_ = 0;
    int run_min_ = 0;
    int run_max_ = 0;
    int value_bits_ = 0;
};

class SingleEdgeRowLenDecoder {
public:
    SingleEdgeRowLenDecoder(int resolution, int d_format, int mbuint_reduce_bits)
        : resolution_(resolution), mbuint_reduce_bits_(mbuint_reduce_bits) {
        static constexpr int bits[] = {2, 3, 4};
        static constexpr int mins[] = {-1, -3, -7};
        if (d_format < 0 || d_format >= 3) {
            throw std::runtime_error("invalid SingleEdge d value format");
        }
        if (mbuint_reduce_bits < 0 || mbuint_reduce_bits > 8) {
            throw std::runtime_error("invalid SingleEdge MBUIntReduce bits");
        }
        d_bits_ = bits[d_format];
        d_min_ = mins[d_format];
    }

    bool hasMbUIntReduce() const { return mbuint_reduce_bits_ > 0; }

    int readToken(ByteReader& reader, int* dest, int limit) const {
        int prefix = static_cast<int>(reader.readBitsAsInt32(1));
        if (prefix == 0) {
            if (limit < 1) {
                throw std::runtime_error("MBUInt token exceeds requested count");
            }
            dest[0] = detail::toInt(reader.readMbUInt(), "SingleEdge MBUInt token");
            return 1;
        }
        return readSingleEdgeToken(reader, dest, limit);
    }

    int readReducedMiddleToken(ByteReader& reader, int* dest, int limit) const {
        int prefix = static_cast<int>(reader.readBitsAsInt32(1));
        if (prefix == 0) {
            if (!hasMbUIntReduce()) {
                throw std::runtime_error("MBUIntReduce is disabled");
            }
            if (limit < 1) {
                throw std::runtime_error("short MBUInt token exceeds requested count");
            }
            dest[0] = static_cast<int>(reader.readBitsAsInt32(mbuint_reduce_bits_)) + 1;
            return 1;
        }
        return readSingleEdgeToken(reader, dest, limit);
    }

private:
    int readSingleEdgeToken(ByteReader& reader, int* dest, int limit) const {
        if (resolution_ != 8 && resolution_ != 16 && resolution_ != 32
            && resolution_ != 64 && resolution_ != 128 && resolution_ != 256) {
            throw std::runtime_error("unsupported SingleEdgeRow resolution");
        }
        int run_count = static_cast<int>(reader.readBitsAsInt32(5)) + 2;
        if (run_count > limit) {
            throw std::runtime_error("single edge token exceeds requested count");
        }
        int previous = detail::toInt(reader.readMbUInt(), "SingleEdge initial value");
        if (previous <= 0) {
            throw std::runtime_error("invalid single edge value");
        }
        dest[0] = previous;
        for (int i = 1; i < run_count; i++) {
            int d_value = static_cast<int>(reader.readBitsAsInt32(d_bits_)) + d_min_;
            int value = detail::toInt(
                static_cast<int64_t>(2) * resolution_ - previous + d_value,
                "SingleEdge value");
            if (value <= 0) {
                throw std::runtime_error("invalid single edge value");
            }
            dest[i] = value;
            previous = value;
        }
        return run_count;
    }

    int resolution_;
    int d_bits_ = 0;
    int d_min_ = 0;
    int mbuint_reduce_bits_ = 0;
};

} // namespace detail

class GaluchatImageDataChunk01Reader {
public:
    explicit GaluchatImageDataChunk01Reader(ByteReader& reader)
    {
        if (detail::readAscii(reader, 4) != "GI01") {
            throw std::runtime_error("invalid GI01 chunk");
        }
        size_t payload_size = detail::toSize(reader.readMbUInt(), "GI01 payload size");
        payload_reader_ = std::make_unique<detail::LimitedReader>(reader, payload_size);
        reader_ = payload_reader_.get();
        width = detail::positiveInt(reader_->readMbUInt(), "GI01 width");
        height = detail::positiveInt(reader_->readMbUInt(), "GI01 height");
        int square_unit_log2 = static_cast<int>(reader_->readByte());
        if (square_unit_log2 > 30) {
            throw std::runtime_error("GI01 squareUnit exponent is out of range");
        }
        square_unit = 1 << square_unit_log2;
        hus = (width - 1) / square_unit + 1;
        vus = (height - 1) / square_unit + 1;
        validateBlockLayout();
    }

    int width = 0;
    int height = 0;
    int square_unit = 0;
    int hus = 0;
    int vus = 0;
    int64_t readPoint(int x, int y) {
        if (x < 0 || y < 0 || x >= width || y >= height) {
            throw std::runtime_error("point is outside image");
        }
        SinglePixelRaster pixel;
        readRect(x, y, pixel);
        return pixel.value;
    }

    RawRaster toRaster() {
        RawRaster raster(width, height);
        readRect(0, 0, raster);
        return raster;
    }

    template <class Raster>
    void readRect(int x, int y, Raster& dest) {
        if (consumed_) throw std::runtime_error("GI01 reader has already been consumed");
        consumed_ = true;
        Rect target{x, y, dest.width, dest.height};
        BlockReader block(*this);
        int count = hus * vus;
        for (int index = 0; index < count; index++) {
            Rect source{(index % hus) * square_unit, (index / hus) * square_unit, square_unit, square_unit};
            Rect crossed{};
            if (!detail::crossRect(source, target, crossed)) {
                block.skipBlock(1);
                continue;
            }
            block.readBlockRect(
                {crossed.x - source.x, crossed.y - source.y, crossed.width, crossed.height},
                dest,
                crossed.x - target.x,
                crossed.y - target.y);
        }
        reader_->skipToByte();
        if (!payload_reader_->atEnd()) {
            throw std::runtime_error("GI01 chunk size does not match decoded blocks");
        }
    }

    void skipToEnd() {
        reader_->skipToByte();
        reader_->skipInByte(payload_reader_->remaining());
        consumed_ = true;
    }

private:
    struct SinglePixelRaster {
        int width = 1;
        int height = 1;
        int64_t value = 0;

        void set(int, int, int64_t next) { value = next; }
    };

    using CellHeader = detail::CellHeader;
    using NodePallet = detail::NodePallet;
    using PalletHeader = detail::PalletHeader;
    using PalletMgr = detail::PalletMgr;
    using PalletValueReader = detail::PalletValueReader;
    using ShortValueRleLenDecoder = detail::ShortValueRleLenDecoder;
    using SingleEdgeRowLenDecoder = detail::SingleEdgeRowLenDecoder;

    struct BlockHeader {
        int compression_type;
        bool palette_delta;
    };

    class BlockReader {
    public:
        explicit BlockReader(const GaluchatImageDataChunk01Reader& owner)
            : owner_(owner), reader_(*owner.reader_) {}

        void skipBlock(int count) {
            for (int i = 0; i < count; i++) {
                BlockHeader header = readBlockHeader(reader_.readByte());
                if (header.compression_type != 0) {
                    size_t size = detail::toSize(
                        reader_.readMbUInt(), "GI01 block payload size");
                    reader_.skipInByte(size);
                    continue;
                }
                PalletValueReader pallet_reader(header.palette_delta);
                CellHeader cell(reader_.readByte());
                PalletMgr pmgr;
                owner_.skipNode(cell, reader_, owner_.square_unit, pallet_reader, pmgr);
                reader_.skipToByte();
            }
        }

        template <class Raster>
        void readBlockRect(const Rect& target, Raster& dest, int dest_x, int dest_y) {
            BlockHeader header = readBlockHeader(reader_.readByte());
            PalletValueReader pallet_reader(header.palette_delta);
            PalletMgr pmgr;
            if (header.compression_type == 0) {
                CellHeader cell(reader_.readByte());
                owner_.readNodeRect(cell, reader_, owner_.square_unit, pallet_reader, pmgr, target, dest, dest_x, dest_y);
                reader_.skipToByte();
                return;
            }
            if (header.compression_type == 1) {
                size_t payload_size = detail::toSize(
                    reader_.readMbUInt(), "GI01 RAWS payload size");
                detail::LimitedReader payload(reader_, payload_size);
                CellHeader cell(payload.readByte());
                owner_.readNodeRect(cell, payload, owner_.square_unit, pallet_reader, pmgr, target, dest, dest_x, dest_y);
                payload.skipToByte();
                if (!payload.atEnd()) {
                    throw std::runtime_error("GI01 block payload has trailing bytes");
                }
                return;
            }
            if (header.compression_type == 2) {
                size_t payload_size = detail::toSize(
                    reader_.readMbUInt(), "GI01 LZSS payload size");
                detail::LimitedReader compressed(reader_, payload_size);
                detail::LzssReader lzss(compressed);
                CellHeader cell(lzss.readByte());
                owner_.readNodeRect(cell, lzss, owner_.square_unit, pallet_reader, pmgr, target, dest, dest_x, dest_y);
                lzss.skipToByte();
                lzss.validateEnd();
                return;
            }
            throw std::runtime_error("unsupported GI01 block compression type");
        }

    private:
        const GaluchatImageDataChunk01Reader& owner_;
        ByteReader& reader_;
    };

    static BlockHeader readBlockHeader(uint8_t byte1) {
        if ((byte1 & 0x4f) != 0) {
            throw std::runtime_error("invalid GI01 BlockHeader reserved bits");
        }
        int compression_type = (byte1 >> 4) & 0x03;
        if (compression_type == 3) {
            throw std::runtime_error("reserved GI01 block compression type");
        }
        return {compression_type, (byte1 & 0x80) != 0};
    }

    void validateBlockLayout() const {
        int count = detail::multiplyInt(hus, vus, "GI01 block count");
        int padded_width = detail::multiplyInt(hus, square_unit, "GI01 padded width");
        int padded_height = detail::multiplyInt(vus, square_unit, "GI01 padded height");
        (void)count;
        detail::multiplyInt(padded_width, padded_height, "GI01 padded pixel count");
    }

    template <class Raster>
    void readNodeRect(
        CellHeader header,
        ByteReader& reader,
        int resolution,
        const PalletValueReader& pallet_reader,
        PalletMgr& pmgr,
        const Rect& target,
        Raster& dest,
        int dest_x,
        int dest_y) const {
        if (header.isNode()) {
            readContainerRect(header, reader, resolution, pallet_reader, pmgr, target, dest, dest_x, dest_y);
        } else if (header.isRaw()) {
            readRawRect(header, reader, resolution, pallet_reader, pmgr, target, dest, dest_x, dest_y);
        } else if (header.isRle()) {
            readRleRect(header, reader, resolution, pallet_reader, pmgr, target, dest, dest_x, dest_y);
        } else {
            throw std::runtime_error("invalid GI01 CellHeader type");
        }
    }

    void skipNode(
        CellHeader header,
        ByteReader& reader,
        int resolution,
        const PalletValueReader& pallet_reader,
        PalletMgr& pmgr) const {
        if (header.isNode()) {
            skipContainer(header, reader, resolution, pallet_reader, pmgr);
        } else if (header.isRaw()) {
            skipRaw(header, reader, resolution, pallet_reader, pmgr);
        } else if (header.isRle()) {
            skipRle(header, reader, resolution, pallet_reader, pmgr);
        } else {
            throw std::runtime_error("invalid GI01 CellHeader type");
        }
    }

    static int readRawPallet(CellHeader header, ByteReader& reader, const PalletValueReader& pallet_reader, PalletMgr& pmgr) {
        int update_low4 = header.rawUpdatePalletTableLow4();
        if (header.palletResolution() == CellHeader::PALLET_4BIT) {
            int update_table = (static_cast<int>(reader.readBitsAsInt32(12)) << 4) | update_low4;
            pallet_reader.applyTable(reader, pmgr, update_table, 16);
            return header.numOfPallet();
        }
        int update_width = header.palletResolution() == CellHeader::PALLET_1BIT ? 2 : 4;
        if (update_low4 >= (1 << update_width)) {
            throw std::runtime_error("RAW/P pallet update table has reserved bits");
        }
        pallet_reader.applyTable(reader, pmgr, update_low4, update_width);
        return header.numOfPallet();
    }

    static int bitWidthForPaletteSize(int size) {
        if (size <= 2) return 1;
        if (size <= 4) return 2;
        if (size <= 16) return 4;
        if (size <= 256) return 8;
        throw std::runtime_error("unsupported palette size");
    }

    static void skipBits(ByteReader& reader, int bit_count) {
        while (bit_count >= 31) {
            reader.readBitsAsInt32(31);
            bit_count -= 31;
        }
        if (bit_count > 0) {
            reader.readBitsAsInt32(bit_count);
        }
    }

    template <class Raster>
    void readRawRect(
        CellHeader header,
        ByteReader& reader,
        int resolution,
        const PalletValueReader& pallet_reader,
        PalletMgr& pmgr,
        const Rect& target,
        Raster& dest,
        int dest_x,
        int dest_y) const {
        if (!header.hasValidRawReservedBits()) {
            throw std::runtime_error("RAW CellHeader reserved bits are not zero");
        }
        int pallet_size = header.palletResolution() == CellHeader::PALLET_NBIT ? 0 : readRawPallet(header, reader, pallet_reader, pmgr);
        int bits = pallet_size == 0 ? 0 : bitWidthForPaletteSize(pallet_size);
        int pixels = resolution * resolution;
        for (int index = 0; index < pixels; index++) {
            int64_t value = pallet_size == 0 ? static_cast<int64_t>(reader.readMbUInt())
                                             : pmgr.getValue(static_cast<int>(reader.readBitsAsInt32(bits)));
            int lx = index % resolution;
            int ly = index / resolution;
            if (detail::insideRect(target, lx, ly)) {
                dest.set(lx - target.x + dest_x, ly - target.y + dest_y, value);
            }
        }
    }

    void skipRaw(CellHeader header, ByteReader& reader, int resolution, const PalletValueReader& pallet_reader, PalletMgr& pmgr) const {
        if (!header.hasValidRawReservedBits()) {
            throw std::runtime_error("RAW CellHeader reserved bits are not zero");
        }
        int pixels = resolution * resolution;
        if (header.palletResolution() == CellHeader::PALLET_NBIT) {
            for (int i = 0; i < pixels; i++) {
                reader.readMbUInt();
            }
            return;
        }
        int pallet_size = readRawPallet(header, reader, pallet_reader, pmgr);
        skipBits(reader, pixels * bitWidthForPaletteSize(pallet_size));
    }

    static PalletHeader readRlePacketHeader(CellHeader header, ByteReader& reader, const PalletValueReader& pallet_reader, PalletMgr& pmgr) {
        if (!header.hasValidRleReservedBits()) {
            throw std::runtime_error("RLE CellHeader data encoding is reserved");
        }
        PalletHeader pallet_header = PalletHeader::readFrom(reader, header.palletResolution());
        int encoding = header.rleDataEncoding();
        if (encoding == CellHeader::RLE_DATA_ENCODING_SINGLE_EDGE_ROW && pallet_header.value_bits_add > 14) {
            throw std::runtime_error("RLE SingleEdgeRow EncodingParams is reserved");
        }
        if (encoding == CellHeader::RLE_DATA_ENCODING_SHORT_VALUE && pallet_header.value_bits_add > 0x07) {
            throw std::runtime_error("RLE ShortValue EncodingParams is reserved");
        }
        if (encoding != CellHeader::RLE_DATA_ENCODING_SHORT_VALUE
            && encoding != CellHeader::RLE_DATA_ENCODING_SINGLE_EDGE_ROW
            && pallet_header.value_bits_add != 0) {
            throw std::runtime_error("RLE PalletHeader encoding params must be zero");
        }
        if (pallet_header.update_pallet_table > 0) {
            pallet_reader.applyTable(reader, pmgr, pallet_header.update_pallet_table, pallet_header.capacity);
        }
        return pallet_header;
    }

    static int readNextIndex(ByteReader& reader, int pallet_mode, const PalletHeader& header, int run_index, int previous_index, bool has_previous) {
        if (pallet_mode == CellHeader::RLE_PALLET_2) {
            return (header.initial_index + run_index) % 2;
        }
        if (pallet_mode == CellHeader::RLE_PALLET_3 || pallet_mode == CellHeader::RLE_PALLET_5) {
            if (run_index == 0) {
                return header.initial_index;
            }
            if (!has_previous) {
                throw std::runtime_error("previous index is required");
            }
            int bits = pallet_mode == CellHeader::RLE_PALLET_3 ? 1 : 2;
            int mod = pallet_mode == CellHeader::RLE_PALLET_3 ? 3 : 5;
            return (previous_index + static_cast<int>(reader.readBitsAsInt32(bits)) + 1) % mod;
        }
        if (pallet_mode == CellHeader::RLE_PALLET_16) {
            return static_cast<int>(reader.readBitsAsInt32(4));
        }
        throw std::runtime_error("invalid RLE pallet mode");
    }

    template <class Consumer>
    static void iterRleRuns(ByteReader& reader, int resolution, int pallet_mode, int data_encoding, int value_bits_add, const PalletHeader& pallet_header, Consumer consumer) {
        int pixels = resolution * resolution;
        int run_index = 0;
        int previous_index = 0;
        bool has_previous = false;
        int total = 0;
        auto emit = [&](int count) {
            if (count <= 0) {
                throw std::runtime_error("RLE count must be positive");
            }
            if (count > pixels - total) {
                throw std::runtime_error("RLE count total exceeds resolution");
            }
            total += count;
            int pallet_index = readNextIndex(reader, pallet_mode, pallet_header, run_index, previous_index, has_previous);
            previous_index = pallet_index;
            has_previous = true;
            run_index++;
            consumer(count, pallet_index);
        };

        if (data_encoding == CellHeader::RLE_DATA_ENCODING_MBUINT) {
            while (total < pixels) {
                emit(detail::toInt(reader.readMbUInt(), "RLE count"));
            }
            return;
        }

        int explicit_count;
        std::array<int, 67> token_buffer{};
        if (data_encoding == CellHeader::RLE_DATA_ENCODING_SHORT_VALUE) {
            ShortValueRleLenDecoder codec(resolution, value_bits_add & 0x03, (value_bits_add >> 2) & 0x01);
            int run_count = detail::toInt(reader.readMbUInt(), "ShortValue run count");
            if (run_count <= 0) {
                throw std::runtime_error("ShortValue requires at least one value");
            }
            explicit_count = run_count - 1;
            while (run_index < explicit_count) {
                int token_count = codec.readToken(reader, token_buffer.data(), explicit_count - run_index);
                for (int i = 0; i < token_count; i++) {
                    if (total + token_buffer[i] >= pixels) {
                        throw std::runtime_error("invalid RLE count total");
                    }
                    emit(token_buffer[i]);
                }
            }
        } else if (data_encoding == CellHeader::RLE_DATA_ENCODING_SINGLE_EDGE_ROW) {
            int reduce_code = value_bits_add % 5;
            int reduce_bits = reduce_code == 0 ? 0 : reduce_code + 1;
            SingleEdgeRowLenDecoder codec(resolution, value_bits_add / 5, reduce_bits);
            int run_count = detail::toInt(reader.readMbUInt(), "SingleEdgeRow run count");
            if (run_count < 2) {
                throw std::runtime_error("SingleEdgeRow requires at least two values");
            }
            explicit_count = run_count - 1;
            if (codec.hasMbUIntReduce()) {
                emit(detail::toInt(reader.readMbUInt(), "SingleEdgeRow first count"));
                while (run_index < explicit_count) {
                    int token_count = codec.readReducedMiddleToken(reader, token_buffer.data(), explicit_count - run_index);
                    for (int i = 0; i < token_count; i++) {
                        if (total + token_buffer[i] >= pixels) {
                            throw std::runtime_error("invalid RLE count total");
                        }
                        emit(token_buffer[i]);
                    }
                }
            } else {
                while (run_index < explicit_count) {
                    int token_count = codec.readToken(reader, token_buffer.data(), explicit_count - run_index);
                    for (int i = 0; i < token_count; i++) {
                        if (total + token_buffer[i] >= pixels) {
                            throw std::runtime_error("invalid RLE count total");
                        }
                        emit(token_buffer[i]);
                    }
                }
            }
        } else {
            throw std::runtime_error("invalid RLE data encoding");
        }
        int last = pixels - total;
        if (last <= 0) {
            throw std::runtime_error("RLE count total does not leave final run");
        }
        emit(last);
    }

    template <class Raster>
    void readRleRect(
        CellHeader header,
        ByteReader& reader,
        int resolution,
        const PalletValueReader& pallet_reader,
        PalletMgr& pmgr,
        const Rect& target,
        Raster& dest,
        int dest_x,
        int dest_y) const {
        PalletHeader pallet_header = readRlePacketHeader(header, reader, pallet_reader, pmgr);
        int max_index = -1;
        int position = 0;
        iterRleRuns(reader, resolution, header.palletResolution(), header.rleDataEncoding(), pallet_header.value_bits_add, pallet_header,
            [&](int count, int pallet_index) {
                if (pallet_index > max_index) {
                    max_index = pallet_index;
                }
                int64_t value = pmgr.getValue(pallet_index);
                for (int i = 0; i < count; i++) {
                    int mapped = detail::mapIndex(resolution, header.rleMode(), position++);
                    int lx = mapped % resolution;
                    int ly = mapped / resolution;
                    if (detail::insideRect(target, lx, ly)) {
                        dest.set(lx - target.x + dest_x, ly - target.y + dest_y, value);
                    }
                }
            });
        if (max_index >= header.numOfPallet()) {
            throw std::runtime_error("RLE pallet index exceeds palette size");
        }
    }

    void skipRle(CellHeader header, ByteReader& reader, int resolution, const PalletValueReader& pallet_reader, PalletMgr& pmgr) const {
        PalletHeader pallet_header = readRlePacketHeader(header, reader, pallet_reader, pmgr);
        int max_index = -1;
        iterRleRuns(reader, resolution, header.palletResolution(), header.rleDataEncoding(), pallet_header.value_bits_add, pallet_header,
            [&](int, int pallet_index) {
                if (pallet_index > max_index) {
                    max_index = pallet_index;
                }
            });
        if (max_index >= header.numOfPallet()) {
            throw std::runtime_error("RLE pallet index exceeds palette size");
        }
    }

    template <class Raster>
    void readContainerRect(
        CellHeader header,
        ByteReader& reader,
        int resolution,
        const PalletValueReader& pallet_reader,
        PalletMgr& pmgr,
        const Rect& target,
        Raster& dest,
        int dest_x,
        int dest_y) const {
        if (!header.hasValidContainerHeader()) {
            throw std::runtime_error("invalid ContainerNode CellHeader");
        }
        int half = resolution / 2;
        if (header.containerType() == CellHeader::CONTAINER_TYPE_MONO) {
            pallet_reader.applyTable(reader, pmgr, header.updatePalletTable4(), 4);
            detail::fillRect(dest, dest_x, dest_y, target.width, target.height, pmgr.getValue(0));
            return;
        }
        int mask = reader.readByte();
        pallet_reader.applyTable(reader, pmgr, header.updatePalletTable4(), 4);
        NodePallet node_pallet{mask, header.containerType(), {pmgr.table[0], pmgr.table[1], pmgr.table[2], pmgr.table[3]}};
        for (int index = 0; index < 4; index++) {
            int hx = (index % 2) * half;
            int hy = (index / 2) * half;
            int cx = hx > target.x ? hx : target.x;
            int cy = hy > target.y ? hy : target.y;
            int cr = (hx + half) < (target.x + target.width) ? (hx + half) : (target.x + target.width);
            int cb = (hy + half) < (target.y + target.height) ? (hy + half) : (target.y + target.height);
            bool has_crossed = cx < cr && cy < cb;
            int64_t value = 0;
            if (node_pallet.palletValue(index, value)) {
                if (has_crossed) {
                    detail::fillRect(dest, dest_x + cx - target.x, dest_y + cy - target.y, cr - cx, cb - cy, value);
                }
                continue;
            }
            CellHeader child(reader.readByte());
            if (!has_crossed) {
                skipNode(child, reader, half, pallet_reader, pmgr);
            } else {
                readNodeRect(child, reader, half, pallet_reader, pmgr, {cx - hx, cy - hy, cr - cx, cb - cy}, dest, dest_x + cx - target.x, dest_y + cy - target.y);
            }
        }
    }

    void skipContainer(CellHeader header, ByteReader& reader, int resolution, const PalletValueReader& pallet_reader, PalletMgr& pmgr) const {
        if (!header.hasValidContainerHeader()) {
            throw std::runtime_error("invalid ContainerNode CellHeader");
        }
        if (header.containerType() == CellHeader::CONTAINER_TYPE_MONO) {
            pallet_reader.applyTable(reader, pmgr, header.updatePalletTable4(), 4);
            return;
        }
        int mask = reader.readByte();
        pallet_reader.applyTable(reader, pmgr, header.updatePalletTable4(), 4);
        NodePallet node_pallet{mask, header.containerType(), {pmgr.table[0], pmgr.table[1], pmgr.table[2], pmgr.table[3]}};
        for (int index = 0; index < 4; index++) {
            int64_t value = 0;
            if (node_pallet.palletValue(index, value)) {
                continue;
            }
            skipNode(CellHeader(reader.readByte()), reader, resolution / 2, pallet_reader, pmgr);
        }
    }

    std::unique_ptr<detail::LimitedReader> payload_reader_;
    ByteReader* reader_ = nullptr;
    bool consumed_ = false;
};

class GaluchatWGSMap3Reader {
public:
    explicit GaluchatWGSMap3Reader(const std::vector<uint8_t>& bytes)
        : GaluchatWGSMap3Reader(
            std::make_shared<BufferReaderFactory>(bytes)) {}

    GaluchatWGSMap3Reader(const uint8_t* bytes, size_t size)
        : GaluchatWGSMap3Reader(
            std::make_shared<BufferReaderFactory>(bytes, size)) {}

    explicit GaluchatWGSMap3Reader(std::shared_ptr<const ReaderFactory> factory)
        : factory_(std::move(factory)) {
        std::unique_ptr<ByteReader> reader = factory_->create();
        if (detail::readAscii(*reader, 4) != "GLCH") {
            throw std::runtime_error("invalid WGSMap header chunk name");
        }
        size_t payload_size = detail::toSize(
            reader->readMbUInt(), "WGSMap header payload size");
        detail::LimitedReader payload(*reader, payload_size);
        if (detail::readBStrAscii(payload, 16) != "WGSMap/3") {
            throw std::runtime_error("GaluchatWGSMap3Reader requires WGSMap/3");
        }
        unit_inv_x = detail::positiveInt(payload.readMbUInt(), "WGSMap unit_inv_x");
        unit_inv_y = detail::positiveInt(payload.readMbUInt(), "WGSMap unit_inv_y");
        west = detail::toInt(payload.readMbInt(), "WGSMap west");
        south = detail::toInt(payload.readMbInt(), "WGSMap south");
        size_t metadata_size = detail::toSize(
            payload.readMbUInt(), "WGSMap metadata size");
        payload.skipInByte(metadata_size);
        if (!payload.atEnd()) {
            throw std::runtime_error("WGSMap header has trailing bytes");
        }
        gi01_offset_ = reader->pos();
        GaluchatImageDataChunk01Reader chunk(*reader);
        width = chunk.width;
        height = chunk.height;
        chunk.skipToEnd();
        if (!reader->atEnd()) {
            throw std::runtime_error("WGSMap/3 has trailing bytes");
        }
    }

    Rect area() const {
        return {west, south, width, height};
    }

    DoubleRect areaOfWgs() const {
        return {
            static_cast<double>(west) / unit_inv_x,
            static_cast<double>(south) / unit_inv_y,
            static_cast<double>(width) / unit_inv_x,
            static_cast<double>(height) / unit_inv_y,
        };
    }

    bool readPoint(int x, int y, int64_t& value) const {
        if (x < 0 || y < 0 || x >= width || y >= height) {
            return false;
        }
        std::unique_ptr<ByteReader> reader = factory_->create(gi01_offset_);
        GaluchatImageDataChunk01Reader gi01(*reader);
        value = gi01.readPoint(x, y);
        return true;
    }

    bool readWgsPoint(int ix, int iy, int64_t& value) const {
        return readPoint(
            detail::subtractInt(ix, west, "WGSMap point x"),
            detail::subtractInt(iy, south, "WGSMap point y"),
            value);
    }

    bool readWgsPoint(double longitude, double latitude, int64_t& value) const {
        return readWgsPoint(
            detail::roundedInt(longitude * unit_inv_x, "WGSMap longitude"),
            detail::roundedInt(latitude * unit_inv_y, "WGSMap latitude"),
            value);
    }

    template <class Raster>
    void readRect(int x, int y, Raster& dest) const {
        std::unique_ptr<ByteReader> reader = factory_->create(gi01_offset_);
        GaluchatImageDataChunk01Reader gi01(*reader);
        gi01.readRect(x, y, dest);
    }

    RawRaster readRect(int x, int y, int rect_width, int rect_height) const {
        RawRaster result(rect_width, rect_height);
        readRect(x, y, result);
        return result;
    }

    template <class Raster>
    void readWgsRect(const Rect& target, Raster& dest) const {
        if (target.width != dest.width || target.height != dest.height) {
            throw std::runtime_error("raster dimensions do not match target rectangle");
        }
        readRect(
            detail::subtractInt(target.x, west, "WGSMap rectangle x"),
            detail::subtractInt(target.y, south, "WGSMap rectangle y"),
            dest);
    }

    RawRaster readWgsRect(const Rect& target) const {
        RawRaster result(target.width, target.height);
        readWgsRect(target, result);
        return result;
    }

    template <class Raster>
    void readWgsRectf(const DoubleRect& target, Raster& dest) const {
        readWgsRect(toGridRect(target), dest);
    }

    RawRaster readWgsRectf(const DoubleRect& target) const {
        return readWgsRect(toGridRect(target));
    }

    RawRaster toRaster() const {
        return readRect(0, 0, width, height);
    }

    int unit_inv_x = 0;
    int unit_inv_y = 0;
    int west = 0;
    int south = 0;
    int width = 0;
    int height = 0;
private:
    Rect toGridRect(const DoubleRect& target) const {
        return {
            detail::roundedInt(target.x * unit_inv_x, "WGSMap rectangle x"),
            detail::roundedInt(target.y * unit_inv_y, "WGSMap rectangle y"),
            detail::roundedInt(target.width * unit_inv_x, "WGSMap rectangle width"),
            detail::roundedInt(target.height * unit_inv_y, "WGSMap rectangle height"),
        };
    }

    std::shared_ptr<const ReaderFactory> factory_;
    size_t gi01_offset_ = 0;
};

class GaluchatWGSMapSet3Reader {
public:
    explicit GaluchatWGSMapSet3Reader(const std::vector<uint8_t>& bytes)
        : GaluchatWGSMapSet3Reader(
            std::make_shared<BufferReaderFactory>(bytes)) {}

    GaluchatWGSMapSet3Reader(const uint8_t* bytes, size_t size)
        : GaluchatWGSMapSet3Reader(
            std::make_shared<BufferReaderFactory>(bytes, size)) {}

    explicit GaluchatWGSMapSet3Reader(
        std::shared_ptr<const ReaderFactory> factory)
        : factory_(std::move(factory)) {
        std::unique_ptr<ByteReader> reader = factory_->create();
        if (detail::readAscii(*reader, 4) != "GLCH") {
            throw std::runtime_error("invalid WGSMapSet header chunk name");
        }

        size_t payload_size = detail::toSize(
            reader->readMbUInt(), "WGSMapSet header payload size");
        detail::LimitedReader payload(*reader, payload_size);

        if (detail::readBStrAscii(payload, 16) != "WGSMapSet/3") {
            throw std::runtime_error("GaluchatWGSMapSet3Reader requires WGSMapSet/3");
        }
        unit_inv_x = detail::positiveInt(payload.readMbUInt(), "WGSMapSet unit_inv_x");
        unit_inv_y = detail::positiveInt(payload.readMbUInt(), "WGSMapSet unit_inv_y");
        size_t metadata_size = detail::toSize(
            payload.readMbUInt(), "WGSMapSet metadata size");
        if (metadata_size > payload.remaining()) {
            throw std::runtime_error("WGSMapSet metadata exceeds header size");
        }
        metadata = detail::readAscii(payload, metadata_size);
        size_t map_count = detail::toSize(
            payload.readMbUInt(), "WGSMapSet map count");
        if (map_count == 0) {
            throw std::runtime_error("WGSMapSet must contain at least one map");
        }
        if (map_count > payload.remaining() / 2) {
            throw std::runtime_error("WGSMapSet map count exceeds header size");
        }

        origins_.reserve(map_count);
        for (size_t i = 0; i < map_count; i++) {
            origins_.push_back({
                detail::toInt(payload.readMbInt(), "WGSMapSet west"),
                detail::toInt(payload.readMbInt(), "WGSMapSet south"),
            });
        }
        if (!payload.atEnd()) {
            throw std::runtime_error("WGSMapSet header has trailing bytes");
        }

        chunk_offset_ = reader->pos();
        std::string chunk_name = detail::readAscii(*reader, 4);
        if (chunk_name == "LAYO") {
            size_t layout_size = detail::toSize(
                reader->readMbUInt(), "WGSMapSet layout size");
            reader->skipInByte(layout_size);
            chunk_offset_ = reader->pos();
            chunk_name = detail::readAscii(*reader, 4);
        }
        if (chunk_name != "GI01") {
            throw std::runtime_error("WGSMapSet/3 does not contain a GI01 chunk");
        }

        std::unique_ptr<ByteReader> chunks = factory_->create(chunk_offset_);
        int west = origins_[0].west;
        int south = origins_[0].south;
        int east = west;
        int north = south;
        for (const Origin& origin : origins_) {
            GaluchatImageDataChunk01Reader chunk(*chunks);
            west = origin.west < west ? origin.west : west;
            south = origin.south < south ? origin.south : south;
            int chunk_east = detail::addInt(origin.west, chunk.width, "WGSMapSet east");
            int chunk_north = detail::addInt(origin.south, chunk.height, "WGSMapSet north");
            east = chunk_east > east ? chunk_east : east;
            north = chunk_north > north ? chunk_north : north;
            chunk.skipToEnd();
        }
        if (!chunks->atEnd()) {
            throw std::runtime_error("WGSMapSet/3 has trailing bytes");
        }
        area_ = {
            west,
            south,
            detail::subtractInt(east, west, "WGSMapSet width"),
            detail::subtractInt(north, south, "WGSMapSet height"),
        };
    }

    bool readWgsPoint(int ix, int iy, int64_t& value) const {
        bool found = false;

        std::unique_ptr<ByteReader> reader = factory_->create(chunk_offset_);
        for (const Origin& origin : origins_) {
            GaluchatImageDataChunk01Reader chunk(*reader);
            int east = detail::addInt(origin.west, chunk.width, "WGSMapSet east");
            int north = detail::addInt(origin.south, chunk.height, "WGSMapSet north");
            if (ix < origin.west || iy < origin.south
                || ix >= east || iy >= north) {
                chunk.skipToEnd();
                continue;
            }
            int64_t current = chunk.readPoint(
                detail::subtractInt(ix, origin.west, "WGSMapSet point x"),
                detail::subtractInt(iy, origin.south, "WGSMapSet point y"));
            chunk.skipToEnd();
            found = true;
            if (current != 0) {
                value = current;
                return true;
            }
        }

        if (found) {
            value = 0;
        }
        return found;
    }

    bool readWgsPoint(double longitude, double latitude, int64_t& value) const {
        return readWgsPoint(
            detail::roundedInt(longitude * unit_inv_x, "WGSMapSet longitude"),
            detail::roundedInt(latitude * unit_inv_y, "WGSMapSet latitude"),
            value);
    }

    Rect area() const { return area_; }

    DoubleRect areaOfWgs() const {
        return {
            static_cast<double>(area_.x) / unit_inv_x,
            static_cast<double>(area_.y) / unit_inv_y,
            static_cast<double>(area_.width) / unit_inv_x,
            static_cast<double>(area_.height) / unit_inv_y,
        };
    }

    template <class Raster>
    void readWgsRect(const Rect& target, Raster& dest) const {
        validateRasterTarget(target, dest);
        detail::fillRect(dest, 0, 0, dest.width, dest.height, 0);

        std::unique_ptr<ByteReader> reader = factory_->create(chunk_offset_);
        for (const Origin& origin : origins_) {
            GaluchatImageDataChunk01Reader chunk(*reader);
            Rect map_area{origin.west, origin.south, chunk.width, chunk.height};
            Rect crossed{};
            if (!detail::crossRect(map_area, target, crossed)) {
                chunk.skipToEnd();
                continue;
            }
            ZeroFilteredRasterView<Raster> filtered(
                dest,
                crossed.x - target.x,
                crossed.y - target.y,
                crossed.width,
                crossed.height);
            chunk.readRect(
                detail::subtractInt(crossed.x, origin.west, "WGSMapSet rectangle x"),
                detail::subtractInt(crossed.y, origin.south, "WGSMapSet rectangle y"),
                filtered);
            chunk.skipToEnd();
        }
    }

    RawRaster readWgsRect(const Rect& target) const {
        RawRaster result(target.width, target.height);
        readWgsRect(target, result);
        return result;
    }

    template <class Raster>
    void readWgsRectf(const DoubleRect& target, Raster& dest) const {
        readWgsRect(toGridRect(target), dest);
    }

    RawRaster readWgsRectf(const DoubleRect& target) const {
        return readWgsRect(toGridRect(target));
    }

    template <class Raster>
    void readRect(int x, int y, Raster& dest) const {
        readWgsRect({
            detail::addInt(area_.x, x, "WGSMapSet rectangle x"),
            detail::addInt(area_.y, y, "WGSMapSet rectangle y"),
            dest.width,
            dest.height,
        }, dest);
    }

    RawRaster readRect(int x, int y, int width, int height) const {
        RawRaster result(width, height);
        readRect(x, y, result);
        return result;
    }

    RawRaster toRaster() const {
        return readWgsRect(area_);
    }

    size_t mapCount() const { return origins_.size(); }

    int unit_inv_x = 0;
    int unit_inv_y = 0;
    std::string metadata;

private:
    struct Origin {
        int west;
        int south;
    };

    template <class Raster>
    class ZeroFilteredRasterView {
    public:
        ZeroFilteredRasterView(
            Raster& parent,
            int parent_x,
            int parent_y,
            int view_width,
            int view_height)
            : width(view_width),
              height(view_height),
              parent_(parent),
              parent_x_(parent_x),
              parent_y_(parent_y) {}

        void set(int x, int y, int64_t value) {
            if (value != 0) {
                parent_.set(parent_x_ + x, parent_y_ + y, value);
            }
        }

        int width;
        int height;

    private:
        Raster& parent_;
        int parent_x_;
        int parent_y_;
    };

    template <class Raster>
    static void validateRasterTarget(const Rect& target, const Raster& dest) {
        if (target.width < 0 || target.height < 0
            || target.width != dest.width || target.height != dest.height) {
            throw std::runtime_error("raster dimensions do not match target rectangle");
        }
    }

    Rect toGridRect(const DoubleRect& target) const {
        return {
            detail::roundedInt(target.x * unit_inv_x, "WGSMapSet rectangle x"),
            detail::roundedInt(target.y * unit_inv_y, "WGSMapSet rectangle y"),
            detail::roundedInt(target.width * unit_inv_x, "WGSMapSet rectangle width"),
            detail::roundedInt(target.height * unit_inv_y, "WGSMapSet rectangle height"),
        };
    }

    std::shared_ptr<const ReaderFactory> factory_;
    std::vector<Origin> origins_;
    size_t chunk_offset_ = 0;
    Rect area_{0, 0, 0, 0};
};

} // namespace galuchat
