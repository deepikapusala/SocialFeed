"""
FastAPI Application Factory (Stage A).

Implements the official application factory create_app(), lifespan management,
middleware stack, error envelope mapping, and route registration.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.health import router as health_router
from app.api.feed import router as feed_router
from app.api.posts import router as posts_router
from app.api.users import router as users_router
from app.api.search import router as search_router
from app.common.dependencies import get_request_id
from app.common.errors import (
    AppException,
    CODE_INTERNAL_ERROR,
    CODE_NOT_FOUND,
    CODE_VALIDATION_ERROR,
    CODE_CONFLICT,
    CODE_SERVICE_UNAVAILABLE,
    format_error_envelope,
)
from app.common.middleware import REQUEST_ID_HEADER, RequestIdMiddleware
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI Lifespan management.
    Validates configuration at startup and releases resources at shutdown.
    Does not connect to a database or perform heavy import operations at startup.
    """
    # 1. Startup: Load and validate runtime configuration
    _ = get_settings()
    yield
    # 2. Shutdown: Resource cleanup
    from app.database import dispose_async_engine
    await dispose_async_engine()


def create_app() -> FastAPI:
    """
    Application factory constructing a fully configured FastAPI application.
    """
    settings = get_settings()

    app = FastAPI(
        title="Instagram Clone API",
        description="Stage A Deterministic In-Memory FastAPI Backend",
        version="1.0.0",
        lifespan=lifespan,
    )

    # 1. Register Middlewares
    # Note: Starlette executes middleware in reverse addition order.
    # CORSMiddleware added first, then RequestIdMiddleware added outermost.
    allowed_origins = [o.strip() for o in settings.FRONTEND_ORIGIN.split(",") if o.strip()]
    for dev_origin in ("http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"):
        if dev_origin not in allowed_origins:
            allowed_origins.append(dev_origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[REQUEST_ID_HEADER],
    )
    app.add_middleware(RequestIdMiddleware)

    # 2. Exception Handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        req_id = get_request_id(request)
        envelope = format_error_envelope(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=req_id,
        ) 
        return JSONResponse(
            status_code=exc.status_code,
            content=envelope,
            headers={REQUEST_ID_HEADER: req_id},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        req_id = get_request_id(request)
        errors = exc.errors()
        details = []
        is_body_error = False

        for err in errors:
            loc = err.get("loc", ())
            loc_type = loc[0] if loc else "unknown"
            if loc_type == "body":
                is_body_error = True
            field_name = str(loc[-1]) if loc else "unknown"
            details.append(
                {
                    "field": field_name,
                    "reason": err.get("type", "invalid"),
                    "message": err.get("msg", ""),
                }
            )

        status_code = 422 if is_body_error else 400
        message = details[0]["message"] if details and details[0].get("message") else "Request validation failed"
        envelope = format_error_envelope(
            code=CODE_VALIDATION_ERROR,
            message=message,
            details=details,
            request_id=req_id,
        )
        return JSONResponse(
            status_code=status_code,
            content=envelope,
            headers={REQUEST_ID_HEADER: req_id},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        req_id = get_request_id(request)
        code_map = {
            400: CODE_VALIDATION_ERROR,
            404: CODE_NOT_FOUND,
            409: CODE_CONFLICT,
            503: CODE_SERVICE_UNAVAILABLE,
        }
        code = code_map.get(
            exc.status_code,
            CODE_INTERNAL_ERROR if exc.status_code >= 500 else CODE_VALIDATION_ERROR,
        )
        details = exc.detail if isinstance(exc.detail, list) else []
        message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        envelope = format_error_envelope(
            code=code,
            message=message,
            details=details,
            request_id=req_id,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=envelope,
            headers={REQUEST_ID_HEADER: req_id},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        req_id = get_request_id(request)
        envelope = format_error_envelope(
            code=CODE_INTERNAL_ERROR,
            message="An internal server error occurred",
            details=[],
            request_id=req_id,
        )
        return JSONResponse(
            status_code=500,
            content=envelope,
            headers={REQUEST_ID_HEADER: req_id},
        )

    # 3. Register Routers
    app.include_router(health_router)
    app.include_router(feed_router) 
    app.include_router(posts_router)
    app.include_router(users_router)
    app.include_router(search_router)

    return app


# Root ASGI application instance for ASGI servers (e.g. uvicorn app.main:app)
app = create_app()
