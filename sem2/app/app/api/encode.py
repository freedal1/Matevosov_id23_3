from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
from app.services.huffman import huffman_encode
from app.services.xor import xor_encrypt

router = APIRouter()

class EncodeRequest(BaseModel):
    text: str
    key: str

class EncodeResponse(BaseModel):
    encoded_data: str
    key: str
    huffman_codes: dict
    padding: int

class DecodeRequest(BaseModel):
    encoded_data: str
    key: str
    huffman_codes: dict
    padding: int

class DecodeResponse(BaseModel):
    decoded_text: str

@router.post("/encode", response_model=EncodeResponse)
async def encode(request: EncodeRequest):
    try:
        # First, apply Huffman encoding
        encoded_text, huffman_codes, padding = huffman_encode(request.text)
        
        # Then, apply XOR encryption
        encrypted_text = xor_encrypt(encoded_text, request.key)
        
        # Convert to base64 for safe transmission
        encoded_data = base64.b64encode(encrypted_text.encode()).decode()
        
        return EncodeResponse(
            encoded_data=encoded_data,
            key=request.key,
            huffman_codes=huffman_codes,
            padding=padding
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/decode", response_model=DecodeResponse)
async def decode(request: DecodeRequest):
    try:
        # Decode from base64
        encrypted_text = base64.b64decode(request.encoded_data).decode()
        
        # Apply XOR decryption
        decrypted_text = xor_encrypt(encrypted_text, request.key)
        
        # Remove padding
        decrypted_text = decrypted_text[:-request.padding] if request.padding > 0 else decrypted_text
        
        # Decode Huffman
        decoded_text = ""
        current_code = ""
        reverse_codes = {v: k for k, v in request.huffman_codes.items()}
        
        for bit in decrypted_text:
            current_code += bit
            if current_code in reverse_codes:
                decoded_text += reverse_codes[current_code]
                current_code = ""
        
        return DecodeResponse(decoded_text=decoded_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 