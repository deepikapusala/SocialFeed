# labs/raw_asgi/app.py

import json

MOCK_POSTS = [
    {"id": 1, "author": "Alice", "content": "Hello from ASGI!"},
    {"id": 2, "author": "Bob", "content": "Second mock post."},
]


async def app(scope, receive, send):
    # This toy lab only supports HTTP requests.
    if scope["type"] != "http":
        return

    method = scope["method"]
    path = scope["path"]

    if method == "GET" and path == "/health/live":
        body = json.dumps({"status": "ok"}).encode("utf-8")

        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", b"application/json"),
            ],
        })

        await send({
            "type": "http.response.body",
            "body": body,
        })

    elif method == "GET" and path == "/feed":
        body = json.dumps({"posts": MOCK_POSTS}).encode("utf-8")

        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", b"application/json"),
            ],
        })

        await send({
            "type": "http.response.body",
            "body": body,
        })

    else:
        body = json.dumps({"error": "Not Found"}).encode("utf-8")

        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [
                (b"content-type", b"application/json"),
            ],
        })

        await send({
            "type": "http.response.body",
            "body": body,
        })