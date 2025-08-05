from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request
from jwt.exceptions import InvalidTokenError
from app.db.session import local_session
from app.models.rbac import Endpoint
from sqlalchemy import and_
from app.utils.helper import get_payload
from app.services.logging_services import LoggingService
from app.config.settings import settings

logger = LoggingService(__name__).get_logger()

class RBACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        if settings.TESTING:
            logger.info(f"Testing True in settings, bypassing RBAC check")
            return await call_next(request)

        '''fetch details from request header'''
        auth_header = request.headers.get("Authorization")
        request_method = request.method.upper()
        request_endpoint = request.url.path

        logger.info(f"RBAC check initiated: {request_method} {request_endpoint}")
        
        '''allow docs and authentication API to proceed without authentication'''
        if request_endpoint in ["/docs", "/openapi.json", "/redoc", "/auth/login", "/auth/refresh-token", "/auth/logout", "/orders/payment-success"]:
            logger.debug(f"Bypassing RBAC for endpoint: {request_endpoint}")
            return await call_next(request)
        '''allow registration api to proceed without authentication'''
        if ((request_endpoint in ["/doctor", "/nurse", "/patient"]) and request_method == "POST"):
            logger.debug("Bypassing RBAC for registration endpoint")
            return await call_next(request)

        session = local_session()
        try:
            if not auth_header:
                logger.warning("Authorization header missing")
                return JSONResponse(
                    status_code=401,
                    content="Authorization header missing"
                )

            '''fetch details from token'''
            token = auth_header.split(" ")[1]
            payload = get_payload(token)
            role = payload.get('role')
            token_type = payload.get('type')

            logger.debug(f"Token user role: {role}, token type: {token_type}")

            # Verify only access token proceeds further
            if token_type != 'access':
                logger.warning(f"Invalid token type used: {token_type}")
                return JSONResponse(
                    status_code=401,
                    content=f"Invalid Token Type"
                )

            # Ensure user has access for specific endpoint and method from RBAC table
            end_point = session.query(Endpoint).filter(
                and_(
                    (Endpoint.endpoint == request_endpoint),
                    (Endpoint.methods.any(request_method)),
                    (Endpoint.roles.any(role))
                )
            ).first()

            if not end_point:
                logger.warning(f"Access denied for role '{role}' on {request_method} {request_endpoint}")
                return JSONResponse(
                    status_code=403,
                    content=f"'{role}' do not have permission to call {request_method} {request_endpoint} API"
                )

            logger.info(f"Access granted for role '{role}' to {request_method} {request_endpoint}")
        
        except InvalidTokenError as e:
            logger.error("Invalid token encountered", exc_info=True)
            return JSONResponse(
                status_code=401,
                content=f"{e}"
            )

        except Exception as e:
            logger.exception("Unexpected error in RBAC middleware")
            return JSONResponse(
                status_code=500,
                content="Internal Server Error in RBAC Middleware"
            )
        finally:
            session.close()
            logger.debug("DB session closed for RBACMiddleware")

        return await call_next(request)
