from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging

from httpx import request

logger = logging.getLogger("uvicorn.access")
logger.disabled = True
app = FastAPI()

def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def log_request_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        message = f"{request.method} {request.url.path} completed_in={process_time:.2f}s status_code={response.status_code}"
        print(message)  
        return response
    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

    app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"])