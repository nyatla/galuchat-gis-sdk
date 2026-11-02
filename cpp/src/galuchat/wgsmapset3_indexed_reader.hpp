#pragma once

#include "wgsmap3_reader.hpp"

namespace galuchat {

// The caller can reject oversized datasets before allocating the chunk index.
class MapCountLimitExceeded : public std::runtime_error {
public:
    MapCountLimitExceeded(size_t count, size_t limit)
        : std::runtime_error("WGSMapSet map count exceeds configured limit"), count(count), limit(limit) {}
    const size_t count;
    const size_t limit;
};

// Opt-in indexed access. The sequential reader remains an independent class.
class GaluchatWGSMapSet3IndexedReader {
public:
    explicit GaluchatWGSMapSet3IndexedReader(
        const std::vector<uint8_t>& bytes,
        size_t max_maps = std::numeric_limits<size_t>::max())
        : GaluchatWGSMapSet3IndexedReader(
            std::make_shared<BufferReaderFactory>(bytes), max_maps) {}

    GaluchatWGSMapSet3IndexedReader(
        const uint8_t* bytes, size_t size,
        size_t max_maps = std::numeric_limits<size_t>::max())
        : GaluchatWGSMapSet3IndexedReader(
            std::make_shared<BufferReaderFactory>(bytes, size), max_maps) {}

    explicit GaluchatWGSMapSet3IndexedReader(
        std::shared_ptr<const ReaderFactory> factory,
        size_t max_maps = std::numeric_limits<size_t>::max())
        : factory_(std::move(factory)) {
        std::unique_ptr<ByteReader> reader = factory_->create();
        if (detail::readAscii(*reader, 4) != "GLCH") {
            throw std::runtime_error("invalid WGSMapSet header chunk name");
        }

        size_t payload_size = detail::toSize(
            reader->readMbUInt(), "WGSMapSet header payload size");
        detail::LimitedReader payload(*reader, payload_size);

        if (detail::readBStrAscii(payload, 16) != "WGSMapSet/3") {
            throw std::runtime_error("GaluchatWGSMapSet3IndexedReader requires WGSMapSet/3");
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

        if (map_count > max_maps) {
            throw MapCountLimitExceeded(map_count, max_maps);
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
        for (Origin& origin : origins_) {
            origin.offset = detail::addSize(chunk_offset_, chunks->pos(), "WGSMapSet chunk offset");
            GaluchatImageDataChunk01Reader chunk(*chunks);
            origin.width = chunk.width;
            origin.height = chunk.height;
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
        readWgsRectImpl(target, dest, TailMode::Consume);
    }

    // Same composition as readWgsRect, without traversing each chunk's tail.
    // Needed blocks are fully decoded and validated; unused tails are not.
    template <class Raster>
    void readWgsRectWithoutTail(const Rect& target, Raster& dest) const {
        readWgsRectImpl(target, dest, TailMode::Leave);
    }

    RawRaster readWgsRectWithoutTail(const Rect& target) const {
        RawRaster result(target.width, target.height);
        readWgsRectWithoutTail(target, result);
        return result;
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
        int width = 0;
        int height = 0;
        size_t offset = 0;
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

    enum class TailMode { Consume, Leave };

    template <class Raster>
    void readWgsRectImpl(const Rect& target, Raster& dest, TailMode tail) const {
        validateRasterTarget(target, dest);
        detail::fillRect(dest, 0, 0, dest.width, dest.height, 0);

        for (const Origin& origin : origins_) {
            Rect map_area{origin.west, origin.south, origin.width, origin.height};
            Rect crossed{};
            if (!detail::crossRect(map_area, target, crossed)) continue;
            std::unique_ptr<ByteReader> reader = factory_->create(origin.offset);
            GaluchatImageDataChunk01Reader chunk(*reader);
            ZeroFilteredRasterView<Raster> filtered(
                dest,
                crossed.x - target.x,
                crossed.y - target.y,
                crossed.width,
                crossed.height);
            int x = detail::subtractInt(crossed.x, origin.west, "WGSMapSet rectangle x");
            int y = detail::subtractInt(crossed.y, origin.south, "WGSMapSet rectangle y");
            if (tail == TailMode::Consume) {
                chunk.readRect(x, y, filtered);
                chunk.skipToEnd();
            } else {
                chunk.readRectWithoutTail(x, y, filtered);
                // Each chunk has its own reader; do not seek over the unused tail.
            }
        }
    }

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
