# Raw ASGI Application Lab (Stage A1)

This lab implements a minimal, low-level **ASGI 3.0** compliant callable without any high-level web framework (no FastAPI, no Flask, no Django). It serves as an educational foundation to understand how Python web servers (like Uvicorn) communicate with asynchronous applications.

---

## 1. WSGI vs. ASGI: Core Differences

### What is WSGI?
**WSGI (Web Server Gateway Interface - PEP 3333)** is the traditional Python standard for web applications (e.g., Flask, Django 1.x, Gunicorn).
- **Synchronous & Blocking**: A WSGI application callable has the signature `application(environ, start_response)`.
- It processes requests synchronously on a single thread. If a request waits for I/O (e.g. database query, network call), that thread is blocked until the operation finishes.
- WSGI has no native protocol support for asynchronous coroutines, WebSockets, or long-polling without complex extensions.

### What is ASGI?
**ASGI (Asynchronous Server Gateway Interface)** is the modern standard designed to succeed WSGI.
- **Asynchronous & Message-Driven**: An ASGI application is an async callable with the signature:
  ```python
  async def app(scope, receive, send) -> None:
      ...
  ```
- It natively runs on the Python `asyncio` event loop. While one request waits for non-blocking I/O (`await asyncio.sleep(...)`, async database queries), the event loop can process other concurrent requests on the same thread.
- ASGI supports multiple protocol connection types: HTTP requests, WebSockets, and server Lifespan events.

| Feature | WSGI | ASGI |
|---|---|---|
| **Callable Signature** | `def app(environ, start_response)` | `async def app(scope, receive, send)` |
| **Concurrency Model** | Multi-thread / Multi-process (blocking) | Async Event Loop (`asyncio`) (non-blocking) |
| **Protocols Supported** | Synchronous HTTP/1.1 | HTTP/1.1, HTTP/2, WebSockets, Lifespan |
| **Example Servers** | Gunicorn (sync worker), uWSGI | Uvicorn, Hypercorn, Daphne |
| **Example Frameworks** | Flask, Classic Django, Bottle | FastAPI, Starlette, Quart, Django 3+ |

---

## 2. What Does Uvicorn Do?

- **Uvicorn** is a lightning-fast **ASGI Web Server** implementation built on `uvloop` and `httptools`.
- **Role**: Uvicorn listens on a network socket (TCP/IP), parses raw HTTP bytes into structured dictionaries, opens connection lifecycles, calls your ASGI application, and writes formatted HTTP response bytes back across the socket.
- **Uvicorn vs. FastAPI**:
  - *Uvicorn* is the **server** (handles sockets, protocols, networking, ASGI event dispatching).
  - *FastAPI* is the **application framework** (handles URL routing, Pydantic schema validation, dependency injection, OpenAPI documentation, and exception handling on top of the ASGI interface).

---

## 3. The ASGI Trio: `scope`, `receive`, and `send`

Every ASGI interaction centers around three parameters:

1. **`scope` (dict)**:
   - A dictionary containing metadata describing the incoming connection.
   - For HTTP: Contains `scope["type"] = "http"`, `method` (e.g., `"GET"`), `path` (e.g., `"/health/live"`), `headers`, `query_string`, `client` IP, etc.
   - For Lifespan: Contains `scope["type"] = "lifespan"`.

2. **`receive` (async callable)**:
   - An `async` function (`message = await receive()`) used by the application to listen for incoming event messages from the server.
   - For HTTP: Receives `http.request` messages containing chunks of request body bytes.
   - For Lifespan: Receives `lifespan.startup` and `lifespan.shutdown` events.

3. **`send` (async callable)**:
   - An `async` function (`await send(message)`) used by the application to send event messages back to the server.
   - For HTTP: The application sends two sequential messages:
     1. `http.response.start`: Includes the HTTP status code (e.g., `200`) and response headers.
     2. `http.response.body`: Includes the response body bytes (e.g., JSON payload) and `more_body: False`.
   - For Lifespan: Sends `lifespan.startup.complete` or `lifespan.shutdown.complete`.

---

## 4. HTTP Request Flow in Raw ASGI

```text
[Browser / HTTP Client]
         │ (HTTP GET /health/live)
         ▼
    [Uvicorn Server]
         │ 1. Parses HTTP bytes into `scope` dict:
         │    {"type": "http", "method": "GET", "path": "/health/live", ...}
         │ 2. Invokes: await app(scope, receive, send)
         ▼
   [app.py: app()]
         │ 3. Inspects scope["path"] -> matches "/health/live"
         │ 4. Prepares JSON body: b'{"status": "ok"}'
         │ 5. Sends response start message:
         │    await send({"type": "http.response.start", "status": 200, "headers": [...]})
         │ 6. Sends response body message:
         │    await send({"type": "http.response.body", "body": b'{"status":"ok"}', "more_body": False})
         ▼
    [Uvicorn Server]
         │ 7. Formats HTTP/1.1 200 OK wire bytes and transmits over socket
         ▼
[Browser / HTTP Client receives JSON response]
```

---

## 5. Running the Raw ASGI Lab

To run this raw ASGI lab independently on port `8001` (leaving the main port `8000` free for the FastAPI application):

```bash
# From the backend directory:
cd backend
uvicorn labs.raw_asgi.app:app --port 8001 --reload
```

### Testing Endpoints:
```bash
# 1. Health check (returns HTTP 200)
curl http://localhost:8001/health/live

# 2. Toy feed demonstration (returns HTTP 200)
curl http://localhost:8001/feed

# 3. Unknown route (returns HTTP 404)
curl http://localhost:8001/some-unknown-path
```

---

## 6. Running Automated Tests

Run the dedicated test suite for this lab:

```bash
# Direct Python execution:
python labs/raw_asgi/test_raw_asgi.py

# Or via pytest:
pytest labs/raw_asgi/test_raw_asgi.py -v
```
