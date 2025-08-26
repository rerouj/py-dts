from fastapi import APIRouter, Depends
from starlette.requests import Request

from dts_api.model.RootModel import RootModel
from dts_api.settings.settings import Settings, get_settings

router = APIRouter()

@router.get('/', response_model=RootModel, description="Root endpoint")
def get_root(request: Request, settings: Settings = Depends(get_settings)):

    return RootModel(
        context=settings.dts_context,
        dts_version=settings.dts_version,
        id=f"{request.url}",
        collection="%scollection/{?id,page,nav}" % request.url,
        navigation="%snavigation/{?resource,ref,start,end,down,tree,page}" % request.url,
        document="%sdocument/{?resource,ref,start,end,tree,mediaType}" % request.url
    )