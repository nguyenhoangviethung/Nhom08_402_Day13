from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Xóa contextvars cũ để tránh lọt dữ liệu giữa các request
        clear_contextvars()

        # 2. Lấy x-request-id từ header hoặc tạo mới (định dạng req-xxxxxxxx)
        correlation_id = request.headers.get("x-request-id", f"req-{uuid.uuid4().hex[:8]}")
        
        # 3. Gắn correlation_id vào structlog để mọi dòng log sau này đều có nó
        bind_contextvars(correlation_id=correlation_id)
        
        request.state.correlation_id = correlation_id
        
        start = time.perf_counter()
        response = await call_next(request)
        
        # 4. Trả ID và thời gian xử lý về cho Client qua Header
        process_time_ms = int((time.perf_counter() - start) * 1000)
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = str(process_time_ms)
        
        return response

