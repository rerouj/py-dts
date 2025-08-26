from typing import Union

from fastapi import APIRouter
from starlette.responses import JSONResponse

from dts_api.deps.selectors import service_selector
from dts_api.model.CollectionModel import Collection, CollectionResource, CollectionResourcePagination
from dts_api.model.ParameterModel import *

router = APIRouter()

@router.get("", response_model=Union[Collection, CollectionResource, CollectionResourcePagination], response_model_exclude_none=True, description="Collection endpoint")
def get(query: collection_params, service: service_selector):
    representation: Collection = service.get(query)
    return JSONResponse(content=representation.model_dump(exclude_none=True, exclude_unset=True, by_alias=True), media_type="Content-Type: application/ld+json")

@router.post("", response_model=Collection, description="Post collection endpoint")
def post(query: post_collection_params, service: service_selector):
    representation: Collection = service.post(query)
    return representation

@router.patch("", description="Patch collection endpoint")
def patch(query: post_collection_params, service: service_selector):
    representation: Collection = service.patch(query)
    return representation

@router.delete("", description="Delete collection endpoint")
def delete(query: delete_collection_params, service: service_selector):
    representation: Collection = service.delete(query)
    return representation