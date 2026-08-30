#pragma once

#include <cstdint>
#include <fstream>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "wgsmap3_reader.hpp"

namespace galuchat {

/** Buffered ByteReader backed by a standard C++ binary input stream. */
class FileBufferedReader final : public ByteReader {
public:
    FileBufferedReader(
        const std::string& path,
        size_t source_size,
        size_t offset,
        size_t buffer_size)
        : file_(path, std::ios::binary),
          length_(0),
          buffer_(buffer_size) {
        if (!file_) throw std::runtime_error("cannot open: " + path);
        if (offset > source_size || buffer_size == 0) {
            throw std::runtime_error("invalid file reader parameters");
        }
        length_ = source_size - offset;
        file_.seekg(static_cast<std::streamoff>(offset), std::ios::beg);
        if (!file_) throw std::runtime_error("cannot seek: " + path);
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
        if (length > 0) {
            file_.seekg(static_cast<std::streamoff>(length), std::ios::cur);
            if (!file_) throw std::runtime_error("file seek failed");
            pos_ += length;
        }
    }

private:
    void refill() {
        size_t count = length_ - pos_;
        if (count > buffer_.size()) count = buffer_.size();
        file_.read(reinterpret_cast<char*>(buffer_.data()), static_cast<std::streamsize>(count));
        size_t actual = static_cast<size_t>(file_.gcount());
        if (actual == 0) throw std::runtime_error("unexpected end of byte stream");
        buffer_pos_ = 0;
        buffer_end_ = actual;
    }

    std::ifstream file_;
    size_t length_;
    std::vector<uint8_t> buffer_;
    size_t pos_ = 0;
    size_t buffer_pos_ = 0;
    size_t buffer_end_ = 0;
};

/** ReaderFactory for seekable files available through the C++ standard library. */
class FileReaderFactory final : public ReaderFactory {
public:
    explicit FileReaderFactory(std::string path, size_t buffer_size = 8192)
        : path_(std::move(path)), buffer_size_(buffer_size), size_(fileSize(path_)) {
        if (buffer_size_ == 0) throw std::runtime_error("buffer size must be positive");
    }

    std::unique_ptr<ByteReader> create(size_t offset = 0) const override {
        if (offset > size_) throw std::runtime_error("invalid reader offset");
        return std::make_unique<FileBufferedReader>(path_, size_, offset, buffer_size_);
    }

private:
    static size_t fileSize(const std::string& path) {
        std::ifstream file(path, std::ios::binary | std::ios::ate);
        if (!file) throw std::runtime_error("cannot open: " + path);
        std::streamoff size = file.tellg();
        if (size < 0) throw std::runtime_error("cannot get file size: " + path);
        return static_cast<size_t>(size);
    }

    std::string path_;
    size_t buffer_size_;
    size_t size_;
};

} // namespace galuchat
