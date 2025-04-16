import heapq
from collections import defaultdict
from typing import Dict, Tuple

class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def build_frequency_dict(text: str) -> Dict[str, int]:
    frequency = defaultdict(int)
    for char in text:
        frequency[char] += 1
    return frequency

def build_huffman_tree(frequency: Dict[str, int]) -> HuffmanNode:
    heap = [HuffmanNode(char=char, freq=freq) for char, freq in frequency.items()]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)
    
    return heap[0]

def build_huffman_codes(node: HuffmanNode, code: str = "", codes: Dict[str, str] = None) -> Dict[str, str]:
    if codes is None:
        codes = {}
    
    if node.char is not None:
        codes[node.char] = code
        return codes
    
    build_huffman_codes(node.left, code + "0", codes)
    build_huffman_codes(node.right, code + "1", codes)
    return codes

def encode_text(text: str, codes: Dict[str, str]) -> str:
    return "".join(codes[char] for char in text)

def decode_text(encoded_text: str, codes: Dict[str, str]) -> str:
    reverse_codes = {v: k for k, v in codes.items()}
    current_code = ""
    decoded_text = ""
    
    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_codes:
            decoded_text += reverse_codes[current_code]
            current_code = ""
    
    return decoded_text

def huffman_encode(text: str) -> Tuple[str, Dict[str, str], int]:
    frequency = build_frequency_dict(text)
    tree = build_huffman_tree(frequency)
    codes = build_huffman_codes(tree)
    encoded_text = encode_text(text, codes)
    
    # Calculate padding needed to make the length a multiple of 8
    padding = (8 - len(encoded_text) % 8) % 8
    encoded_text += "0" * padding
    
    return encoded_text, codes, padding 