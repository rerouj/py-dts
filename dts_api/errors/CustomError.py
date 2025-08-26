from urllib.error import URLError

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from dts_api.model.Error import ErrorDict, BaseErrorMessage

async def not_found_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    error_message_type = {
        404: {
            'type': "not_found",
            'message': "Resource not found."
        },
        400: {
            'type': "bad_request",
            'message': "Bad request."
        },
    }
    e_dict = ErrorDict(
        code=exc.status_code,
        type=error_message_type[exc.status_code]['type'],
        message= error_message_type[exc.status_code]['message'],
        details=exc.detail
    )
    model = BaseErrorMessage(error=e_dict)

    return JSONResponse(
        status_code=404,
        content=model.model_dump(),
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for err in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in err["loc"]),  # e.g., query.age
            "message": err["msg"],
            "type": err["type"]
        })

    e_dict = ErrorDict(
        code=422,
        type="validation_error",
        message= "Invalid request parameters.",
        details=errors
    )
    model = BaseErrorMessage(error=e_dict)

    return JSONResponse(
        status_code=422,
        content=model.model_dump(),
    )


async def value_error_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    e_dict = ErrorDict(
        code=400,
        type="bad_request",
        message="Bad request.",
        details=str(exc)
    )
    model = BaseErrorMessage(error=e_dict)

    return JSONResponse(
        status_code=400,
        content=model.model_dump(),
    )

async def connection_error_exception_handler(request: Request, exc: URLError):
    e_dict = ErrorDict(
        code=500,
        type="bad_connection",
        message="Connection error.",
        details=[{"reason": exc.reason, "filename": exc.filename}]
    )
    model = BaseErrorMessage(error=e_dict)

    return JSONResponse(
        status_code=500,
        content=model.model_dump(),
    )