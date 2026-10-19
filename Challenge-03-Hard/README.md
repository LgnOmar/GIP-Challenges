# Challenge 03: Hard - Flash Sale Backend API

A minimal REST API for an online store running a flash sale, with atomic inventory management, transactional order creation, and database-enforced idempotency.

---

## Technology Stack

| Component | Choice | Rationale |
| :--- | :--- | :--- |
| Framework | FastAPI | Already available, fast, auto-validates input, auto-generates Swagger docs |
| Database | SQLite (WAL mode) | Zero infrastructure, built into Python, WAL allows concurrent reads during writes |
| Auth | `X-User-Id` header | Simple header-based identification per the challenge spec |
| Idempotency | `Idempotency-Key` header + DB constraint | `PRIMARY KEY (user_id, key)` enforces uniqueness at database level |

---

## API Endpoints

| Method | Endpoint | Headers Required | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/products` | None | List all products and available stock |
| `GET` | `/products/{id}` | None | View a single product |
| `POST` | `/orders` | `X-User-Id`, `Idempotency-Key` | Place an order (product_id + quantity in body) |
| `GET` | `/orders` | `X-User-Id` | List orders belonging to the authenticated user |

---

## Inventory Concurrency Strategy

1. **`BEGIN IMMEDIATE`** acquires a write lock at transaction start, serializing all writers. Readers (via WAL mode) are not blocked.
2. **Atomic conditional UPDATE**: `UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?`. If `rowcount == 0`, stock was insufficient and the transaction is rolled back. Stock can never go negative because the `CHECK (stock >= 0)` constraint provides an additional database-level safety net.
3. **Single transaction**: Stock decrement, order insertion, and idempotency key storage all happen inside the same `BEGIN IMMEDIATE ... COMMIT` block. If anything fails, everything rolls back.
4. **busy_timeout = 5000ms**: Concurrent writers wait up to 5 seconds for the lock instead of immediately failing.

## Idempotency Mechanism

1. On `POST /orders`, the server computes a SHA-256 hash of the request body (`product_id` + `quantity`).
2. Inside the write transaction, it checks if an idempotency record exists for `(user_id, key)`.
3. **Key exists + same hash**: Return the cached response (201) without creating a new order or decrementing stock.
4. **Key exists + different hash**: Return 409 Conflict ("key used with different request data").
5. **Key does not exist**: Process the order normally. On success, store the key + response in the same transaction.
6. **Key is not stored on failure**: If the order fails (insufficient stock, product not found), the key is not consumed. The user can retry with corrected data using the same key.
7. **Concurrent duplicate requests**: `BEGIN IMMEDIATE` serializes writers, so two requests with the same key are processed sequentially. The second will always find the cached result.

---

## Setup and Run

### 1. Initialize and Seed the Database

```bash
cd Challenge-03-Hard
python seed.py
```
This creates `flash_sale.db` with 5 sample products.

### 2. Start the Server

```bash
uvicorn main:app --reload --port 8000
```
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`

### 3. Run Automated Tests

```bash
pytest test_api.py -v
```

---

## Manual Testing with cURL

### List Products
```bash
curl http://127.0.0.1:8000/products
```

### View Single Product
```bash
curl http://127.0.0.1:8000/products/1
```

### Place an Order
```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -H "X-User-Id: alice" \
  -H "Idempotency-Key: order-001" \
  -d "{\"product_id\": 1, \"quantity\": 2}"
```

### Retry Same Order (idempotent, returns cached result)
```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -H "X-User-Id: alice" \
  -H "Idempotency-Key: order-001" \
  -d "{\"product_id\": 1, \"quantity\": 2}"
```

### View My Orders
```bash
curl http://127.0.0.1:8000/orders -H "X-User-Id: alice"
```

---

## Test Coverage

| Category | Tests | Description |
| :--- | :--- | :--- |
| Products | 3 | List all, get by ID, 404 for nonexistent |
| Orders (basic) | 6 | Success, stock decrement, invalid qty (0 and negative), nonexistent product, insufficient stock |
| Input validation | 2 | Missing X-User-Id header, missing Idempotency-Key header |
| Idempotency | 3 | Same key + same request (cached), same key + different request (409), same key for different users (independent) |
| Order isolation | 2 | Users see only own orders, empty list for new user |
| Concurrency | 2 | 30 parallel purchases for 15-unit product (exactly 15 succeed, stock=0); 10 parallel retries with same idempotency key (1 order created, all get same result) |

---

## Limitations

- **SQLite write throughput**: Only one writer at a time. Sufficient for a coding challenge but not for a high-throughput production flash sale.
- **No authentication**: Users are identified solely by the `X-User-Id` header with no verification.
- **No idempotency key expiration**: Keys are stored indefinitely. A production system would expire them after a TTL.
- **No pagination**: `GET /products` and `GET /orders` return all records. Fine for challenge-scale data.

---

## Render Deployment Settings

- **Root Directory**: `Challenge-03-Hard`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

