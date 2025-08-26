from fastapi import APIRouter
from starlette.responses import JSONResponse

from dts_api.deps.selectors import service_selector
from dts_api.model.NavigationModel import NavigationModel
from dts_api.model.ParameterModel import navigation_params

router = APIRouter()

@router.get("/", response_model=NavigationModel, description="Navigation get endpoint")
def get(params: navigation_params, service: service_selector):
    representation: NavigationModel = service.get(params)
    return JSONResponse(content=representation.model_dump(by_alias=True, exclude_none=True), media_type="Content-Type: application/json")

@router.post("/", description="Navigation post endpoint")
def post():
    return {"value": "ok"}

@router.patch("/", description="Navigation patch endpoint")
def patch():
    return {"value": "ok"}

@router.delete("/", description="Navigation delete endpoint")
def delete():
    return {"value": "ok"}