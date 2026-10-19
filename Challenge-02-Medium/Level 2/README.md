# Challenge 02: Medium - Level 2

## Secure Authentication Service (Signup, Login & JWT)

A minimal, secure authentication API built with FastAPI, SQLite, bcrypt password hashing, and PyJWT token generation and validation.

---

### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/signup` | Register a new user with email & password | No |
| `POST` | `/login`  | Authenticate user and receive a signed JWT | No |
| `GET`  | `/me`     | Retrieve authenticated user profile | Yes (Bearer Token) |

---

### Features & Security Measures

- **Password Hashing**: Uses `bcrypt` with unique salts. Plaintext passwords are never stored.
- **JWT Issuance & Verification**: Tokens are signed using HS256 with expiration validation (30-minute expiry).
- **Protected Endpoints**: Verified via standard `Authorization: Bearer <token>` headers.
- **Input Validation**: Pydantic models validate emails and enforce password length requirements (>= 6 characters).
- **Error Handling**: Graceful responses for duplicate registrations (409), invalid credentials (401), invalid/expired tokens (401), and malformed requests (422).

---

### Running the Service

1. Start the server using Uvicorn:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
2. Interactive Swagger documentation is available at:
   `http://127.0.0.1:8000/docs`

---

### Manual Testing with cURL

#### 1. Register a new user
```bash
curl -X POST http://127.0.0.1:8000/signup \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"alice@example.com\", \"password\": \"secret123\"}"
```

#### 2. Log in and get JWT
```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"alice@example.com\", \"password\": \"secret123\"}"
```
Copy the `access_token` from the JSON response.

#### 3. Access protected `/me` endpoint
```bash
curl -X GET http://127.0.0.1:8000/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### Automated Tests

Run the test suite using pytest:
```bash
pytest test_auth.py
```

---

### Render Deployment Settings

- **Root Directory**: `Challenge-02-Medium/Level 2`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `JWT_SECRET`: Any secure random string (required in production)
  - `ENVIRONMENT`: `production`

