"""Local verification wrapper; synthetic requests only, never used by the production API.

The browser runner sets DEMO_TRACE/DEMO_CONTROL to temporary files. This wrapper
records synthetic HTTP evidence and can delay or fail a request for recovery checks.
"""

import asyncio
import json
import os
from pathlib import Path

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from assistant_api.main import create_app
from assistant_core.config import load_settings
from assistant_core.service import build_service

settings = load_settings(env_file=None)
service = build_service(settings)
app = create_app(settings=settings, service=service)


@app.middleware("http")
async def record_demo(request: Request, call_next):
    control_path = Path(os.environ["DEMO_CONTROL"])
    control = json.loads(control_path.read_text()) if control_path.exists() else {}
    body = await request.body()
    if request.url.path == "/v1/chat":
        await asyncio.sleep(control.get("delay_s", 0))
        service.rag.llm.fail = bool(control.get("provider_down", False))
    if request.url.path == "/v1/feedback" and control.get("feedback_status"):
        response = JSONResponse({"error": {"code": "demo_failure"}}, status_code=control["feedback_status"])
        content = response.body
    else:
        original = await call_next(request)
        content = b"".join([chunk async for chunk in original.body_iterator])
        response = Response(content, status_code=original.status_code, headers=dict(original.headers))
    record = {
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "body": json.loads(body) if body else None,
        "response": json.loads(content),
    }
    with Path(os.environ["DEMO_TRACE"]).open("a", encoding="utf-8") as trace:
        trace.write(json.dumps(record, ensure_ascii=False) + "\n")
    return response
