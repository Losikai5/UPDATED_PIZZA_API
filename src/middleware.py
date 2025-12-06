from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.middleware import trustedhost, cors
import time
import logging

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

async def log_request_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    return response