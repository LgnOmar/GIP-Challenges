from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
import sqlite3
import bcrypt
import jwt
import datetime
import os
from contextlib import contextmanager

# --- Configuration ---

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development").lower()
SECRET_KEY = os.environ.get("JWT_SECRET")

if not SECRET_KEY:
    if ENVIRONMENT == "production" or os.environ.get("RENDER"):
        raise RuntimeError("JWT_SECRET environment variable is missing in production environment!")
    # Convenient fallback strictly for local development and offline test suites
    SECRET_KEY = "dev-insecure-secret-key-change-in-production"

ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 30
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.environ.get("DB_PATH", str(BASE_DIR / "auth.db"))

# --- Database ---

def init_db(db_path: str = DB_PATH):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()

@contextmanager
def get_db_connection(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# --- Security & Password Utilities ---

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + (
        expires_delta or datetime.timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- Schemas ---

class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password with minimum 6 characters")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- App & Dependencies ---

app = FastAPI(title="Auth Service - Challenge 02 Level 2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=True)

@app.on_event("startup")
def startup_event():
    init_db(DB_PATH)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    with get_db_connection(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, created_at FROM users WHERE id = ?", (int(user_id),))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return dict(row)

# --- Routes ---

@app.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(data: UserSignup):
    normalized_email = data.email.strip().lower()

    with get_db_connection(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (normalized_email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address already registered",
            )

        hashed = hash_password(data.password)
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cursor.execute(
            "INSERT INTO users (email, hashed_password, created_at) VALUES (?, ?, ?)",
            (normalized_email, hashed, now),
        )
        conn.commit()
        user_id = cursor.lastrowid

    return {"id": user_id, "email": normalized_email, "created_at": now}

@app.post("/login", response_model=TokenResponse)
def login(data: UserLogin):
    normalized_email = data.email.strip().lower()

    with get_db_connection(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, hashed_password FROM users WHERE email = ?",
            (normalized_email,),
        )
        row = cursor.fetchone()

        if not row or not verify_password(data.password, row["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token({"sub": str(row["id"]), "email": row["email"]})
        return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
