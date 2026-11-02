from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import logger
from app.core.exceptions import MakhtootatException

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...")
    # Startup tasks: verification of storage directory
    from app.storage.local_storage import LocalStorage
    LocalStorage(settings.UPLOAD_DIR)
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title="Makhtootat - Manuscript HTR & AI Research Platform",
    description=(
        "Production-grade backend for Persian and Arabic handwritten manuscript recognition (HTR/OCR), "
        "pgvector hybrid search, and citation-grounded scholarly AI assistant."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers
@app.exception_handler(MakhtootatException)
async def makhtootat_exception_handler(request: Request, exc: MakhtootatException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    clean_errors = []
    for err in errors:
        clean_errors.append({
            "loc": err.get("loc", []),
            "msg": err.get("msg", ""),
            "type": err.get("type", "")
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error in request payload", "errors": clean_errors},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact the system administrator."},
    )


# Mount API Router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Makhtootat - Manuscript HTR and AI Research Platform",
        "documentation": "/docs",
        "api_v1_prefix": "/api/v1",
        "status": "operational",
    }
