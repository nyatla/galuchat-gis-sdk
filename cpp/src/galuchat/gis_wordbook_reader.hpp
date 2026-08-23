#pragma once

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "wgsmap3_reader.hpp"

namespace galuchat {

/** GisWordBook/0 reader without persistent page or hierarchical indexes. */
class GaluchatGisWordBookReader {
public:
    explicit GaluchatGisWordBookReader(
        const std::vector<uint8_t>& bytes,
        size_t token_cache_size = 64)
        : GaluchatGisWordBookReader(
            std::make_shared<BufferReaderFactory>(bytes), token_cache_size) {}

    GaluchatGisWordBookReader(
        const uint8_t* bytes,
        size_t size,
        size_t token_cache_size = 64)
        : GaluchatGisWordBookReader(
            std::make_shared<BufferReaderFactory>(bytes, size), token_cache_size) {}

    explicit GaluchatGisWordBookReader(
        std::shared_ptr<const ReaderFactory> factory,
        size_t token_cache_size = 64)
        : factory_(std::move(factory)), token_cache_size_(token_cache_size) {
        std::array<ChunkLocation, 4> chunks = readChunkLayout(*factory_);
        token_chunk_ = chunks[1];
        text_chunk_ = chunks[2];
        index_chunk_ = chunks[3];

        {
            std::unique_ptr<ByteReader> reader = factory_->create(chunks[0].data_start);
            readHeader(*reader, chunks[0].size);
        }
        {
            std::unique_ptr<ByteReader> reader = factory_->create(token_chunk_.data_start);
            token_count_ = TokenMapReader(*reader).tokenCount();
        }
        int text_token_bits;
        {
            std::unique_ptr<ByteReader> reader = factory_->create(text_chunk_.data_start);
            TextTableReader text(*reader);
            component_count_ = text.recordCount();
            text_token_bits = text.tokenBits();
        }
        int index_code_bits;
        {
            std::unique_ptr<ByteReader> reader = factory_->create(index_chunk_.data_start);
            HierarchicalIndexReader index(*reader, index_chunk_.size);
            record_count_ = index.recordCount();
            depth_ = index.depth();
            index_code_bits = index.codeBits();
        }
        if (text_token_bits < requiredBits(token_count_)) {
            throw std::runtime_error("TT00 token_bits is smaller than TM00 requires");
        }
        if (index_code_bits < requiredBits(component_count_)) {
            throw std::runtime_error("TI00 code_bits is smaller than TT00 requires");
        }
    }

    static GaluchatGisWordBookReader fromFile(
        const std::string& path,
        size_t buffer_size = 8192,
        size_t token_cache_size = 64) {
        return GaluchatGisWordBookReader(
            std::make_shared<FileReaderFactory>(path, buffer_size),
            token_cache_size);
    }

    size_t recordCount() const { return record_count_; }
    size_t depth() const { return depth_; }
    size_t componentCount() const { return component_count_; }
    const std::string& metadata() const { return metadata_; }

    std::vector<size_t> readCodeSet(size_t index) const {
        std::unique_ptr<ByteReader> reader = factory_->create(index_chunk_.data_start);
        return HierarchicalIndexReader(*reader, index_chunk_.size).readCodeSet(index);
    }

    std::string readComponent(size_t code) const {
        std::vector<std::pair<size_t, std::string>> values =
            readComponents(std::vector<size_t>{code});
        return values[0].second;
    }

    std::vector<std::string> readStringSet(size_t index) const {
        std::vector<size_t> codes = readCodeSet(index);
        std::vector<std::pair<size_t, std::string>> components = readComponents(codes);
        std::vector<std::string> result;
        result.reserve(codes.size());
        for (size_t code : codes) result.push_back(findValue(components, code));
        return result;
    }

    bool readStringSetByCode(int64_t code, std::vector<std::string>& result) const {
        result.clear();
        if (code <= 0) return false;
        result = readStringSet(static_cast<size_t>(code - 1));
        return true;
    }

private:
    static constexpr int PALETTE_SIZE = 15;

    struct ChunkLocation {
        std::string name;
        size_t data_start = 0;
        size_t size = 0;
    };

    struct IndexHeader {
        size_t max_depth = 0;
        size_t record_count = 0;
        int code_bits = 0;
        size_t root_count = 0;
        size_t stream_size = 0;
    };

    static std::array<ChunkLocation, 4> readChunkLayout(const ReaderFactory& factory) {
        static const std::array<const char*, 4> names{{"GW00", "TM00", "TT00", "TI00"}};
        std::array<ChunkLocation, 4> chunks{};
        std::unique_ptr<ByteReader> reader = factory.create();
        for (size_t i = 0; i < names.size(); i++) {
            std::string name = readAscii(*reader, 4);
            size_t size = static_cast<size_t>(reader->readMbUInt());
            if (name != names[i]) throw std::runtime_error("invalid GisWordBook chunk order");
            size_t start = reader->pos();
            if (start > factory.size() || size > factory.size() - start) {
                throw std::runtime_error("GisWordBook chunk exceeds source size");
            }
            chunks[i] = {name, start, size};
            reader->skipInByte(size);
        }
        if (reader->pos() != factory.size()) {
            throw std::runtime_error("GisWordBook has trailing bytes");
        }
        return chunks;
    }

    void readHeader(ByteReader& reader, size_t size) {
        size_t start = reader.pos();
        if (readBStrAscii(reader, 16) != "GisWordBook/0") {
            throw std::runtime_error("unsupported GisWordBook version");
        }
        size_t metadata_size = static_cast<size_t>(reader.readMbUInt());
        std::vector<uint8_t> bytes = reader.readBytes(metadata_size);
        metadata_.assign(reinterpret_cast<const char*>(bytes.data()), bytes.size());
        if (reader.pos() - start != size) throw std::runtime_error("GW00 has trailing bytes");
    }

    class TokenMapReader {
    public:
        explicit TokenMapReader(ByteReader& reader) : reader_(reader) {
            token_count_ = static_cast<size_t>(reader_.readMbUInt());
            page_count_ = static_cast<size_t>(reader_.readMbUInt());
        }

        size_t tokenCount() const { return token_count_; }

        std::vector<std::pair<size_t, std::string>> readTokens(
            const std::vector<size_t>& targets) {
            std::vector<std::pair<size_t, std::string>> result;
            result.reserve(targets.size());
            size_t target_pos = 0;
            size_t token_base = 0;
            size_t previous = 0;
            bool has_previous = false;
            for (size_t page = 0; page < page_count_; page++) {
                if (reader_.readByte() != 0) throw std::runtime_error("unsupported TM00 page header");
                size_t token_size = static_cast<size_t>(reader_.readMbUInt());
                size_t page_tokens = static_cast<size_t>(reader_.readMbUInt());
                size_t stream_size = static_cast<size_t>(reader_.readMbUInt());
                validateTokenPage(token_size, page_tokens, stream_size, previous, has_previous);
                previous = token_size;
                has_previous = true;
                size_t page_end = token_base + page_tokens;
                size_t consumed = 0;
                while (target_pos < targets.size() && targets[target_pos] < page_end) {
                    size_t token_id = targets[target_pos];
                    if (token_id < token_base || token_id >= token_count_) {
                        throw std::runtime_error("TM00 token id out of range");
                    }
                    size_t offset = (token_id - token_base) * token_size;
                    reader_.skipInByte(offset - consumed);
                    std::vector<uint8_t> bytes = reader_.readBytes(token_size);
                    result.push_back({token_id, std::string(
                        reinterpret_cast<const char*>(bytes.data()), bytes.size())});
                    consumed = offset + token_size;
                    target_pos++;
                }
                if (target_pos == targets.size()) return result;
                reader_.skipInByte(stream_size - consumed);
                token_base = page_end;
            }
            throw std::runtime_error("TM00 token id out of range");
        }

    private:
        ByteReader& reader_;
        size_t token_count_ = 0;
        size_t page_count_ = 0;
    };

    class TextTableReader {
    public:
        explicit TextTableReader(ByteReader& reader) : reader_(reader) {
            record_count_ = static_cast<size_t>(reader_.readMbUInt());
            (void)reader_.readMbUInt();
            page_count_ = static_cast<size_t>(reader_.readMbUInt());
            token_bits_ = static_cast<int>(reader_.readMbUInt());
            if (token_bits_ < 1 || token_bits_ > 16) {
                throw std::runtime_error("invalid TT00 token_bits");
            }
        }

        size_t recordCount() const { return record_count_; }
        int tokenBits() const { return token_bits_; }

        std::vector<std::pair<size_t, std::vector<size_t>>> readTokenIdSets(
            const std::vector<size_t>& codes) {
            for (size_t code : codes) {
                if (code >= record_count_) throw std::runtime_error("TT00 code out of range");
            }
            std::vector<std::pair<size_t, std::vector<size_t>>> result;
            size_t target_pos = 0;
            size_t record_base = 0;
            size_t previous = 0;
            bool has_previous = false;
            for (size_t page = 0; page < page_count_; page++) {
                if (reader_.readByte() != 0) throw std::runtime_error("unsupported TT00 page header");
                size_t record_tokens = static_cast<size_t>(reader_.readMbUInt());
                size_t page_records = static_cast<size_t>(reader_.readMbUInt());
                size_t stream_size = static_cast<size_t>(reader_.readMbUInt());
                validateTextPage(record_tokens, page_records, previous, has_previous);
                previous = record_tokens;
                has_previous = true;
                size_t page_end = record_base + page_records;
                size_t target_start = target_pos;
                while (target_pos < codes.size() && codes[target_pos] < page_end) target_pos++;
                if (target_start == target_pos) {
                    reader_.skipInByte(stream_size);
                    record_base = page_end;
                    continue;
                }
                std::vector<size_t> local_targets;
                for (size_t i = target_start; i < target_pos; i++) {
                    local_targets.push_back(codes[i] - record_base);
                }
                size_t stream_start = bitPosition(reader_);
                std::vector<std::pair<size_t, std::vector<size_t>>> local =
                    decodeTargets(reader_, page_records, local_targets, token_bits_);
                for (auto& entry : local) {
                    if (entry.second.size() != record_tokens) {
                        throw std::runtime_error("TT00 record token count mismatch");
                    }
                    entry.first += record_base;
                    result.push_back(std::move(entry));
                }
                if (target_pos == codes.size()) return result;
                size_t consumed = bitPosition(reader_) - stream_start;
                reader_.skipBits(stream_size * 8 - consumed);
                record_base = page_end;
            }
            throw std::runtime_error("TT00 code out of range");
        }

    private:
        ByteReader& reader_;
        size_t record_count_ = 0;
        size_t page_count_ = 0;
        int token_bits_ = 0;
    };

    class HierarchicalIndexReader {
    public:
        HierarchicalIndexReader(ByteReader& reader, size_t size) : reader_(reader) {
            size_t start = reader_.pos();
            header_.max_depth = static_cast<size_t>(reader_.readMbUInt());
            header_.record_count = static_cast<size_t>(reader_.readMbUInt());
            header_.code_bits = static_cast<int>(reader_.readMbUInt());
            header_.root_count = static_cast<size_t>(reader_.readMbUInt());
            header_.stream_size = static_cast<size_t>(reader_.readMbUInt());
            validateIndexHeader(header_);
            if (reader_.pos() - start + header_.stream_size != size) {
                throw std::runtime_error("TI00 has trailing bytes");
            }
        }

        size_t recordCount() const { return header_.record_count; }
        size_t depth() const { return header_.max_depth; }
        int codeBits() const { return header_.code_bits; }

        std::vector<size_t> readCodeSet(size_t target) {
            if (target >= header_.record_count) throw std::runtime_error("TI00 index out of range");
            std::vector<size_t> result(header_.max_depth, 0);
            if (header_.max_depth == 1) readLeafBlocksByCount(header_.root_count, target, result);
            else readPrefixesByCount(0, header_.root_count, target, result);
            return result;
        }

    private:
        void readPrefixesByCount(
            size_t depth, size_t count, size_t target, std::vector<size_t>& out) {
            for (size_t i = 0; i < count; i++) {
                size_t code = reader_.readBitsAsInt32(header_.code_bits);
                size_t leaves = static_cast<size_t>(reader_.readMbUInt());
                size_t payload_bits = static_cast<size_t>(reader_.readMbUInt());
                if (target < leaves) {
                    out[depth] = code;
                    readChildren(depth + 1, leaves, target, out);
                    return;
                }
                skipPayload(depth + 1, leaves, payload_bits);
                target -= leaves;
            }
            throw std::runtime_error("TI00 index not found");
        }

        void readChildren(
            size_t depth, size_t leaves, size_t target, std::vector<size_t>& out) {
            if (depth == header_.max_depth - 1) {
                readLeafBlocksByLeafCount(leaves, target, out);
                return;
            }
            size_t consumed = 0;
            while (consumed < leaves) {
                size_t code = reader_.readBitsAsInt32(header_.code_bits);
                size_t child_leaves = static_cast<size_t>(reader_.readMbUInt());
                size_t payload_bits = static_cast<size_t>(reader_.readMbUInt());
                if (target < consumed + child_leaves) {
                    out[depth] = code;
                    readChildren(depth + 1, child_leaves, target - consumed, out);
                    return;
                }
                skipPayload(depth + 1, child_leaves, payload_bits);
                consumed += child_leaves;
            }
            throw std::runtime_error("TI00 child index not found");
        }

        void readLeafBlocksByCount(
            size_t blocks, size_t target, std::vector<size_t>& out) {
            for (size_t block = 0; block < blocks; block++) {
                size_t leaves = static_cast<size_t>(reader_.readMbUInt());
                if (target < leaves) {
                    reader_.skipBits(target * static_cast<size_t>(header_.code_bits));
                    out[header_.max_depth - 1] = reader_.readBitsAsInt32(header_.code_bits);
                    return;
                }
                reader_.skipBits(leaves * static_cast<size_t>(header_.code_bits));
                target -= leaves;
            }
            throw std::runtime_error("TI00 leaf index not found");
        }

        void readLeafBlocksByLeafCount(
            size_t leaves, size_t target, std::vector<size_t>& out) {
            size_t consumed = 0;
            while (consumed < leaves) {
                size_t block_leaves = static_cast<size_t>(reader_.readMbUInt());
                if (target < consumed + block_leaves) {
                    reader_.skipBits((target - consumed) * static_cast<size_t>(header_.code_bits));
                    out[header_.max_depth - 1] = reader_.readBitsAsInt32(header_.code_bits);
                    return;
                }
                reader_.skipBits(block_leaves * static_cast<size_t>(header_.code_bits));
                consumed += block_leaves;
            }
            throw std::runtime_error("TI00 leaf index not found");
        }

        void skipPayload(size_t depth, size_t leaves, size_t payload_bits) {
            if (payload_bits > 0) reader_.skipBits(payload_bits);
            else skipChildren(depth, leaves);
        }

        void skipChildren(size_t depth, size_t leaves) {
            size_t consumed = 0;
            if (depth == header_.max_depth - 1) {
                while (consumed < leaves) {
                    size_t block_leaves = static_cast<size_t>(reader_.readMbUInt());
                    reader_.skipBits(block_leaves * static_cast<size_t>(header_.code_bits));
                    consumed += block_leaves;
                }
                return;
            }
            while (consumed < leaves) {
                (void)reader_.readBitsAsInt32(header_.code_bits);
                size_t child_leaves = static_cast<size_t>(reader_.readMbUInt());
                size_t payload_bits = static_cast<size_t>(reader_.readMbUInt());
                skipPayload(depth + 1, child_leaves, payload_bits);
                consumed += child_leaves;
            }
        }

        ByteReader& reader_;
        IndexHeader header_;
    };

    std::vector<std::pair<size_t, std::string>> readComponents(
        std::vector<size_t> codes) const {
        std::sort(codes.begin(), codes.end());
        codes.erase(std::unique(codes.begin(), codes.end()), codes.end());
        std::vector<std::pair<size_t, std::vector<size_t>>> token_sets;
        {
            std::unique_ptr<ByteReader> reader = factory_->create(text_chunk_.data_start);
            token_sets = TextTableReader(*reader).readTokenIdSets(codes);
        }
        std::vector<size_t> token_ids;
        for (const auto& entry : token_sets) {
            token_ids.insert(token_ids.end(), entry.second.begin(), entry.second.end());
        }
        std::sort(token_ids.begin(), token_ids.end());
        token_ids.erase(std::unique(token_ids.begin(), token_ids.end()), token_ids.end());

        std::vector<std::pair<size_t, std::string>> resolved;
        std::vector<size_t> missing;
        for (size_t token_id : token_ids) {
            std::string token;
            if (cachedToken(token_id, token)) resolved.push_back({token_id, token});
            else missing.push_back(token_id);
        }
        if (!missing.empty()) {
            std::unique_ptr<ByteReader> reader = factory_->create(token_chunk_.data_start);
            std::vector<std::pair<size_t, std::string>> loaded =
                TokenMapReader(*reader).readTokens(missing);
            resolved.insert(resolved.end(), loaded.begin(), loaded.end());
        }

        std::vector<std::pair<size_t, std::string>> result;
        for (size_t code : codes) {
            const std::vector<size_t>& ids = findValue(token_sets, code);
            std::string value;
            for (size_t token_id : ids) {
                const std::string& token = findValue(resolved, token_id);
                value += token;
                rememberToken(token_id, token);
            }
            result.push_back({code, std::move(value)});
        }
        return result;
    }

    bool cachedToken(size_t token_id, std::string& token) const {
        for (size_t i = 0; i < token_cache_.size(); i++) {
            if (token_cache_[i].first != token_id) continue;
            token = token_cache_[i].second;
            auto entry = token_cache_[i];
            token_cache_.erase(token_cache_.begin() + static_cast<std::ptrdiff_t>(i));
            token_cache_.push_back(std::move(entry));
            return true;
        }
        return false;
    }

    void rememberToken(size_t token_id, const std::string& token) const {
        if (token_cache_size_ == 0) return;
        for (auto it = token_cache_.begin(); it != token_cache_.end(); ++it) {
            if (it->first == token_id) {
                token_cache_.erase(it);
                break;
            }
        }
        token_cache_.push_back({token_id, token});
        if (token_cache_.size() > token_cache_size_) token_cache_.erase(token_cache_.begin());
    }

    static std::vector<std::pair<size_t, std::vector<size_t>>> decodeTargets(
        ByteReader& reader,
        size_t,
        const std::vector<size_t>& targets,
        int token_bits) {
        size_t packets = static_cast<size_t>(reader.readMbUInt());
        std::array<int64_t, PALETTE_SIZE + 1> palette{};
        palette.fill(-1);
        std::vector<std::pair<size_t, std::vector<size_t>>> result;
        std::vector<size_t> current;
        size_t record = 0;
        size_t target_pos = 0;
        size_t target = targets[0];
        for (size_t packet = 0; packet < packets; packet++) {
            int type = static_cast<int>(reader.readBitsAsInt32(2));
            size_t value_bits = static_cast<size_t>(reader.readMbUInt());
            if (type == 0) {
                size_t start = bitPosition(reader);
                int slots = static_cast<int>(reader.readBitsAsInt32(PALETTE_SIZE));
                palette.fill(-1);
                for (int bit = 0; bit < PALETTE_SIZE; bit++) {
                    if ((slots & (1 << bit)) != 0) {
                        palette[static_cast<size_t>(bit + 1)] = reader.readBitsAsInt32(token_bits);
                    }
                }
                assertConsumed(reader, start, value_bits);
            } else if (type == 1) {
                size_t start = bitPosition(reader);
                size_t slot = reader.readBitsAsInt32(4);
                if (slot == 0) throw std::runtime_error("TT00 palette slot zero is reserved");
                palette[slot] = reader.readBitsAsInt32(token_bits);
                assertConsumed(reader, start, value_bits);
            } else if (type == 2) {
                if (value_bits % 4 != 0) throw std::runtime_error("invalid TT00 payload size");
                for (size_t i = 0; i < value_bits / 4; i++) {
                    size_t local = reader.readBitsAsInt32(4);
                    if (local == 0) {
                        if (record == target) {
                            result.push_back({target, std::move(current)});
                            current.clear();
                            target_pos++;
                            if (target_pos == targets.size()) return result;
                            target = targets[target_pos];
                        }
                        record++;
                    } else if (record == target) {
                        if (palette[local] < 0) throw std::runtime_error("TT00 empty palette slot");
                        current.push_back(static_cast<size_t>(palette[local]));
                    }
                }
            } else {
                reader.skipBits(value_bits);
            }
        }
        throw std::runtime_error("TT00 target record terminator not found");
    }

    static void validateTokenPage(
        size_t token_size, size_t count, size_t stream_size,
        size_t previous, bool has_previous) {
        if ((has_previous && token_size < previous) || token_size == 0 || count == 0
            || stream_size != token_size * count) {
            throw std::runtime_error("invalid TM00 token page");
        }
    }

    static void validateTextPage(
        size_t token_count, size_t record_count, size_t previous, bool has_previous) {
        if ((has_previous && token_count < previous) || record_count == 0) {
            throw std::runtime_error("invalid TT00 text page");
        }
    }

    static void validateIndexHeader(const IndexHeader& value) {
        if (value.max_depth == 0 || value.record_count == 0
            || value.code_bits < 1 || value.code_bits > 31
            || value.root_count == 0 || value.stream_size == 0) {
            throw std::runtime_error("invalid TI00 header");
        }
    }

    static int requiredBits(size_t count) {
        int bits = 1;
        while (bits < 63 && (uint64_t{1} << bits) < count) bits++;
        return bits;
    }

    static size_t bitPosition(const ByteReader& reader) {
        return reader.pos() * 8 - static_cast<size_t>(reader.bitOffset());
    }

    static void assertConsumed(ByteReader& reader, size_t start, size_t expected) {
        if (bitPosition(reader) - start != expected) {
            throw std::runtime_error("TT00 packet size mismatch");
        }
    }

    static std::string readAscii(ByteReader& reader, size_t length) {
        std::string result;
        result.reserve(length);
        for (size_t i = 0; i < length; i++) result.push_back(static_cast<char>(reader.readByte()));
        return result;
    }

    static std::string readBStrAscii(ByteReader& reader, size_t length) {
        std::string result = readAscii(reader, length);
        size_t zero = result.find('\0');
        if (zero != std::string::npos) result.resize(zero);
        return result;
    }

    template <class Value>
    static const Value& findValue(
        const std::vector<std::pair<size_t, Value>>& values,
        size_t key) {
        for (const auto& entry : values) {
            if (entry.first == key) return entry.second;
        }
        throw std::runtime_error("decoded value not found");
    }

    std::shared_ptr<const ReaderFactory> factory_;
    ChunkLocation token_chunk_;
    ChunkLocation text_chunk_;
    ChunkLocation index_chunk_;
    size_t token_count_ = 0;
    size_t component_count_ = 0;
    size_t record_count_ = 0;
    size_t depth_ = 0;
    std::string metadata_;
    size_t token_cache_size_ = 0;
    mutable std::vector<std::pair<size_t, std::string>> token_cache_;
};

} // namespace galuchat
