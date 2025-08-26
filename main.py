from contextlib import asynccontextmanager
from urllib.error import URLError

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi

from dts_api.api.route.router import base_router
from dts_api.classes.Cache import Cache
from dts_api.classes.Store import Store
from dts_api.errors.CustomError import validation_exception_handler, not_found_exception_handler, \
    connection_error_exception_handler
from dts_api.settings.settings import OpenapiSettings, get_settings


@asynccontextmanager
async def lifespan(api: FastAPI):
    print("####### startup events #######")
    api.__str__()
    Store()
    Cache()
    print("####### end startup events #######")
    yield

openapi_settings = OpenapiSettings()

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
    exception_handlers={
        RequestValidationError: validation_exception_handler,
        HTTPException: not_found_exception_handler,
        URLError: connection_error_exception_handler
    }
)
app.include_router(base_router, prefix="/api/dts/v1")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="DTS-API: Littérature Apocryphe Chrétienne",
        description="API des éditions du projet ENLAC",
        version="0.1",
        servers=[
            {"url": "http://127.0.0.1:8000", "description": "Localhost"},
            # {"url": "http://ftsr-dev.unil.ch:8082", "description": "ftsr admin server"}
        ],
        contact={"name": "Renato Diaz (FTSR-Unil)", "email": "renato.diaz@unil.ch"},
        routes=app.routes,
        tags=[
                {"name": "root", "description": "Root route, returns global infos."},
                {"name": "collection", "description": "Operations on collection entries"},
                {"name": "navigation", "description": "Operations on navigation entries"},
                {"name": "document", "description": "Operations on document entries"},
            ],
    )
    [openapi_schema["components"]["schemas"].pop(model, None) for model in ["UrlComponent", "CollectionParams", "DocumentParams", "NavigationParams", "IndexMetadataModel"]]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)