#pragma once

#include <FS.h>

#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "wgsmap3_reader.hpp"

namespace galuchat {

/** Buffered ByteReader backed by an Arduino fs::FS file. */
class ArduinoFsBufferedReader final : public ByteReader {
public:
    ArduinoFsBufferedReader(
        fs::FS& file_system,
        const char* path,
        size_t source_size,
        size_t offset,
        size_t buffer_size)
        : file_(file_system.open(path, FILE_READ)),
          length_(0),
          buffer_(buffer_size) {
        if (!file_) throw std::runtime_error("cannot open Arduino file");
        if (offset > source_size || buffer_size == 0) {
            throw std::runtime_error("invalid Arduino file reader parameters");
        }
        length_ = source_size - offset;
        if (!file_.seek(offset, SeekSet)) {
            throw std::runtime_error("cannot seek Arduino file");
        }
    }

    size_t pos() const override { return pos_; }
    bool atEnd() const override { return pos_ == length_; }

protected:
    uint8_t nextByte() override {
        if (pos_ >= length_) throw std::runtime_error("unexpected end of byte stream");
        if (buffer_pos_ >= buffer_end_) refill();
        pos_++;
        return buffer_[buffer_pos_++];
    }

    void skipByte(size_t length) override {
        if (length > length_ - pos_) {
            pos_ = length_;
            buffer_pos_ = buffer_end_;
            throw std::runtime_error("unexpected end of byte stream");
        }
        size_t buffered = buffer_end_ - buffer_pos_;
        if (length <= buffered) {
            buffer_pos_ += length;
            pos_ += length;
            return;
        }
        pos_ += buffered;
        length -= buffered;
        buffer_pos_ = buffer_end_ = 0;
        if (length == 0) return;
        size_t target = file_.position() + length;
        if (!file_.seek(target, SeekSet)) {
            throw std::runtime_error("Arduino file seek failed");
        }
        pos_ += length;
    }

private:
    void refill() {
        size_t count = length_ - pos_;
        if (count > buffer_.size()) count = buffer_.size();
        size_t actual = file_.read(buffer_.data(), count);
        if (actual == 0) throw std::runtime_error("unexpected end of byte stream");
        buffer_pos_ = 0;
        buffer_end_ = actual;
    }

    fs::File file_;
    size_t length_;
    std::vector<uint8_t> buffer_;
    size_t pos_ = 0;
    size_t buffer_pos_ = 0;
    size_t buffer_end_ = 0;
};

/** ReaderFactory that opens an Arduino fs::FS file for every read session. */
class ArduinoFsReaderFactory final : public ReaderFactory {
public:
    ArduinoFsReaderFactory(
        fs::FS& file_system,
        std::string path,
        size_t buffer_size = 4096)
        : file_system_(&file_system),
          path_(std::move(path)),
          buffer_size_(buffer_size),
          size_(fileSize(file_system, path_.c_str())) {
        if (buffer_size_ == 0) throw std::runtime_error("buffer size must be positive");
    }

    std::unique_ptr<ByteReader> create(size_t offset = 0) const override {
        if (offset > size_) throw std::runtime_error("invalid reader offset");
        return std::make_unique<ArduinoFsBufferedReader>(
            *file_system_, path_.c_str(), size_, offset, buffer_size_);
    }

private:
    static size_t fileSize(fs::FS& file_system, const char* path) {
        fs::File file = file_system.open(path, FILE_READ);
        if (!file) throw std::runtime_error("cannot open Arduino file");
        return file.size();
    }

    fs::FS* file_system_;
    std::string path_;
    size_t buffer_size_;
    size_t size_;
};

} // namespace galuchat
