# Crypto API

A FastAPI-based application that provides Huffman encoding and XOR encryption services.

## Features

- User authentication with JWT tokens
- Huffman encoding for data compression
- XOR encryption for data security
- SQLite database for user storage
- RESTful API endpoints

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./sql_app.db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

4. Run the application:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Authentication

- `POST /api/v1/sign-up/` - Register a new user
- `POST /api/v1/login/` - Login and get JWT token
- `GET /api/v1/users/me/` - Get current user information

### Encoding/Decoding

- `POST /api/v1/encode` - Encode text using Huffman and XOR
- `POST /api/v1/decode` - Decode previously encoded text

## Example Usage

### Encoding
```bash
curl -X POST "http://localhost:8000/api/v1/encode" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, World!", "key": "secret"}'
```

### Decoding
```bash
curl -X POST "http://localhost:8000/api/v1/decode" \
     -H "Content-Type: application/json" \
     -d '{"encoded_data": "...", "key": "secret", "huffman_codes": {...}, "padding": 3}'
```

## Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 