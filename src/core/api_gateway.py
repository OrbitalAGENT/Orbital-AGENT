# orbital-agent/src/api_gateway.py
import logging
import json
import time
from functools import wraps
from typing import Dict, List, Optional, Callable, Any
from urllib.parse import urlparse
import jwt
import redis
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp, Receive, Send, Scope

logger = logging.getLogger(__name__)

class APIGatewayError(Exception):
    """Base exception for API gateway failures"""

class RateLimiter:
    def __init__(self, redis_conn, rate_limit: int = 100, window: int = 60):
        self.redis = redis_conn
        self.rate_limit = rate_limit
        self.window = window

    def check_limit(self, client_id: str) -> bool:
        """Token bucket rate limiting implementation"""
        key = f"rate_limit:{client_id}"
        current = self.redis.get(key)
        if current is None:
            self.redis.setex(key, self.window, self.rate_limit - 1)
            return True
        if int(current) > 0:
            self.redis.decrby(key, 1)
            return True
        return False

class JWTValidator:
    def __init__(self, public_key: str):
        self.public_key = serialization.load_pem_public_key(
            public_key.encode()
        )
    
    def validate_token(self, token: str) -> Dict:
        """Validate JWT with RSA public key"""
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=["RS256"],
                options={"verify_aud": False}
            )
            return payload
        except jwt.PyJWTError as e:
            logger.error(f"JWT validation failed: {str(e)}")
            raise APIGatewayError("Invalid authentication token")

class APIGateway(FastAPI):
    def __init__(self, config: Dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.routes = {}
        self.redis = redis.Redis(**config["redis"])
        self._init_security()
        self._add_core_middleware()

    def _init_security(self):
        """Initialize security components"""
        self.jwt_validator = JWTValidator(self.config["jwt_public_key"])
        self.rate_limiter = RateLimiter(
            self.redis,
            rate_limit=self.config.get("rate_limit", 100),
            window=self.config.get("rate_window", 60)
        )

    def _add_core_middleware(self):
        """Add essential middleware stack"""
        self.add_middleware(AuthenticationMiddleware, gateway=self)
        self.add_middleware(RateLimitingMiddleware, gateway=self)
        self.add_middleware(RequestValidationMiddleware)
        self.add_middleware(ResponseProcessingMiddleware)
        self.add_middleware(CORSMiddleware)

    def register_route(self, path: str, service: str, methods: List[str]):
        """Register backend service route"""
        self.routes[path] = {
            "service": service,
            "methods": methods,
            "upstream": self.config["services"][service]
        }
        logger.info(f"Registered route {path} => {service}")

    async def route_handler(self, request: Request):
        """Dynamic routing handler"""
        path = request.url.path
        route_config = self.routes.get(path)
        
        if not route_config:
            raise HTTPException(status_code=404, detail="Endpoint not found")
        
        return await self._proxy_request(request, route_config["upstream"])

    async def _proxy_request(self, request: Request, upstream: str) -> Response:
        """Forward request to backend service"""
        try:
            headers = self._prepare_forward_headers(request)
            body = await request.body()
            
            response = requests.request(
                method=request.method,
                url=f"{upstream}{request.url.path}",
                headers=headers,
                data=body,
                params=request.query_params,
                timeout=self.config.get("timeout", 5.0)
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Backend service error: {str(e)}")
            raise HTTPException(status_code=502, detail="Service unavailable")

    def _prepare_forward_headers(self, request: Request) -> Dict:
        """Sanitize and prepare headers for forwarding"""
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("authorization", None)
        headers["x-forwarded-for"] = request.client.host
        headers["x-api-version"] = self.config["version"]
        return headers

class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, gateway: APIGateway):
        super().__init__(app)
        self.gateway = gateway
        self.security = HTTPBearer()

    async def dispatch(self, request: Request, call_next):
        """Authentication middleware handler"""
        if request.url.path in self.gateway.config["public_routes"]:
            return await call_next(request)
<i class="fl-spin"></i>
