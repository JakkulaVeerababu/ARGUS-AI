import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

class ModelNotFoundError(Exception):
    """Raised when an ONNX model file cannot be loaded or is missing."""
    pass

class InvalidJobDescriptionError(Exception):
    """Raised when the provided job description is empty or fails validation."""
    pass

class EmptyRetrievalError(Exception):
    """Raised when lexical and semantic search return zero candidates."""
    pass

class CSVProcessingError(Exception):
    """Raised when reading or writing ranking CSV reports fails."""
    pass


def register_exception_handlers(app: FastAPI):
    """Registers standard HTTP exception handlers on the FastAPI application instance."""
    
    @app.exception_handler(ModelNotFoundError)
    async def model_not_found_handler(request: Request, exc: ModelNotFoundError):
        logger.error(f"[EXCEPTION] ModelNotFoundError: {str(exc)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": "ModelServiceUnavailable",
                "message": str(exc)
            }
        )

    @app.exception_handler(InvalidJobDescriptionError)
    async def invalid_jd_handler(request: Request, exc: InvalidJobDescriptionError):
        logger.warning(f"[EXCEPTION] InvalidJobDescriptionError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "InvalidJobDescription",
                "message": str(exc)
            }
        )

    @app.exception_handler(EmptyRetrievalError)
    async def empty_retrieval_handler(request: Request, exc: EmptyRetrievalError):
        logger.info(f"[EXCEPTION] EmptyRetrievalError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error": "EmptyRetrievalResults",
                "message": str(exc),
                "results": []
            }
        )

    @app.exception_handler(CSVProcessingError)
    async def csv_processing_handler(request: Request, exc: CSVProcessingError):
        logger.error(f"[EXCEPTION] CSVProcessingError: {str(exc)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "CSVProcessingFailure",
                "message": str(exc)
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.critical(f"[EXCEPTION] Unhandled Exception: {str(exc)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "InternalServerError",
                "message": "An unexpected error occurred while processing your request."
            }
        )
