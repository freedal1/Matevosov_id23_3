#функции для XOR шифрования
def xor_encrypt(text: str, key: str) -> str:
    encrypted = []
    key_length = len(key)
    
    for i, char in enumerate(text):
        key_char = key[i % key_length]
        encrypted_char = chr(ord(char) ^ ord(key_char))
        encrypted.append(encrypted_char)
    
    return "".join(encrypted)

def xor_decrypt(encrypted_text: str, key: str) -> str:
    return xor_encrypt(encrypted_text, key)  # XOR is symmetric 