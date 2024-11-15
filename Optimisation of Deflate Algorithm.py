class LZ77Compressor:
    def __init__(self, base_window_size=32 * 1024, max_window_size=128 * 1024, chunk_size=64 * 1024):
        # Base window size (default 32KB) and max window size (default 128KB)
        self.base_window_size = base_window_size
        self.max_window_size = max_window_size
        self.chunk_size = chunk_size
        self.window_size = self.base_window_size  # This will be dynamically adjusted

        # Fixed lookahead buffer size for LZ77 (maximum match length)
        self.lookahead_buffer_size = 258  

    def calculate_repetitiveness(self, input_data):
        # A simple repetitiveness calculation by counting repeating consecutive characters
        repeat_count = sum([1 for i in range(1, len(input_data)) if input_data[i] == input_data[i - 1]])
        return repeat_count / len(input_data)

    def adaptive_window_size(self, input_data):
        # Adjust window size based on data repetitiveness
        repetitiveness_ratio = self.calculate_repetitiveness(input_data)
        if repetitiveness_ratio > 0.5:
            # Increase window size if data is highly repetitive, capped by max_window_size
            return min(self.max_window_size, self.base_window_size * 2)
        return self.base_window_size  # Default base window size otherwise

    def compress(self, input_data):
        # Dynamically adjust window size based on the input data's repetitiveness
        self.window_size = self.adaptive_window_size(input_data)
        
        i = 0
        compressed_data = []

        while i < len(input_data):
            # Get the search window and lookahead buffer based on current index
            start = max(0, i - self.window_size)
            search_window = input_data[start:i]
            lookahead_buffer = input_data[i:i + self.lookahead_buffer_size]

            # Find the longest match in the search window
            match = self.find_longest_match(search_window, lookahead_buffer)

            if match:
                (match_distance, match_length) = match
                if match_length < len(lookahead_buffer):
                    next_char = lookahead_buffer[match_length]
                else:
                    next_char = ''
                compressed_data.append((1, match_distance, match_length, next_char))
                i += match_length + 1
            else:
                compressed_data.append((0, input_data[i]))
                i += 1

        return compressed_data

    def find_longest_match(self, search_window, lookahead_buffer):
        best_match_distance = -1
        best_match_length = -1

        # Look for the longest match in the search window
        for j in range(len(search_window)):
            match_length = 0
            while (match_length < len(lookahead_buffer) and
                   j + match_length < len(search_window) and
                   search_window[j + match_length] == lookahead_buffer[match_length]):
                match_length += 1

            if match_length > best_match_length:
                best_match_distance = len(search_window) - j
                best_match_length = match_length

        if best_match_length > 0:
            return best_match_distance, best_match_length

        return None

    def compress_with_chunks(self, input_data):
        compressed_data = []
        
        # Process input data in chunks if it's too large
        for chunk_start in range(0, len(input_data), self.chunk_size):
            chunk = input_data[chunk_start:chunk_start + self.chunk_size]
            compressed_chunk = self.compress(chunk)
            compressed_data.extend(compressed_chunk)
        
        return compressed_data


# Decompression function
def decompress(compressed_data):
    decompressed_data = []
    
    for token in compressed_data:
        if token[0] == 1:  # Match found
            match_distance, match_length, next_char = token[1], token[2], token[3]
            start = len(decompressed_data) - match_distance
            
            # Append the matched sequence from the previous decompressed data
            for i in range(match_length):
                decompressed_data.append(decompressed_data[start + i])
            
            # Append the next character if it exists
            if next_char:
                decompressed_data.append(next_char)
        
        else:  # Literal found
            decompressed_data.append(token[1])
    
    # Join and return the fully decompressed data
    return ''.join(decompressed_data)


# Test compression and decompression
def test_compression(compressor, input_data, description):
    compressed_data = compressor.compress_with_chunks(input_data)
    
    # Decompress and validate
    decompressed_data = decompress(compressed_data)
    
    # Rewriting the assert logic without using assert
    if decompressed_data == input_data:
        print(f"{description} Decompression successful. Data matches original.")
    else:
        print(f"{description} Decompression failed. Data does not match original.")


# Example input data for testing
input_data = "abracadabra" * 56  # Example repetitive data

# Testing adaptive window compression
adaptive_compressor = LZ77Compressor(base_window_size=32 * 1024, max_window_size=128 * 1024, chunk_size=64 * 1024)
test_compression(adaptive_compressor, input_data, "Adaptive window")