from enum import Enum
from typing import Annotated, Optional, Self

from fastapi import Query, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, model_validator

from dts_api.model.Validator import out_of_range_int


class NavEnum(str, Enum):
    parents = "parents"
    children = "children"

class CollectionParams(BaseModel):
    id: Optional[str] = None
    page: out_of_range_int = 1
    nav: NavEnum = NavEnum.children
    limit: out_of_range_int = 10
    offset: out_of_range_int = 0


class PostCollectionParams(BaseModel):
    id: str
    body: dict

class DeleteCollectionParams(BaseModel):
    id: str

class NavigationParams(BaseModel):
    resource: str
    ref: str = None
    start: str = None
    end: str = None
    down: out_of_range_int = None
    tree: str = "default"
    page: out_of_range_int = 1
    limit: out_of_range_int = 100
    offset: out_of_range_int = 0

    @model_validator(mode='after')
    def check_param_cohesion(self) -> Self:
        if self.ref and self.start and self.end:
            raise HTTPException(status_code=400, detail="[model validation err] ref can't be used with start and end")
        if self.ref is None and self.start is None and self.end is None and (self.down is None or self.down == 0):
            # raise HTTPException(status_code=400, detail="[model validation err] At least one of the following parameters must be provided: ref, start, end, down, c.f.: https://distributed-text-services.github.io/specifications/versions/unstable/#navigation-endpoint")
            self.down = -1
        if self.ref is None and (self.start is not None or self.end is not None) and self.down == 0:
            raise HTTPException(status_code=400, detail="[model validation err] This milestone can't be reached: un-allowed request c.f.: https://distributed-text-services.github.io/specifications/versions/unstable/#navigation-endpoint")
        if self.ref is None and self.start is not None and self.end is None:
            raise HTTPException(status_code=400, detail="[model validation err] This milestone can't be reached: please provide an end value")
        if self.ref is None and self.start is None and self.end is not None:
            raise HTTPException(status_code=400, detail="[model validation err] This milestone can't be reached: please provide a start value")

        return self

class DocumentParams(BaseModel):
    resource: str
    ref: Optional[str] = Field(default=None)
    start: str = Field(default=None)
    end: str = Field(default=None)
    tree: str = Field(default=None)
    media_type: str = Field(default="text/xml", serialization_alias="mediaType")

    @model_validator(mode='after')
    def start_end_consistency(self) -> Self:
        if self.ref is not None and (self.start is not None or self.end is not None):
            raise self.__validation_error__(["query", "ref"], "ref value provided with start or end value")
        if self.end is not None and self.start is None:
            raise self.__validation_error__(["query", "end"], "end value provided without a start value")
        if self.end is None and self.start is not None:
            raise self.__validation_error__(["query", "start"], "start value provided without an end value")
        if self.tree == 'default':
            raise self.__validation_error__(["query", "tree"], "This identifier can't be provide, please remove the tree parameter to fetch the default citation tree",)
        if self.tree is None:
            self.tree = "default"
        return self

    @staticmethod
    def __validation_error__(loc: list, msg: str, e_type: str = "value_error") -> RequestValidationError:
        return RequestValidationError([{
            "loc": loc,
            "msg": msg,
            "type": e_type
        }])

collection_params = Annotated[CollectionParams, Query()]
navigation_params = Annotated[NavigationParams, Query(...)]
post_collection_params = Annotated[PostCollectionParams, Query(...)]
delete_collection_params = Annotated[DeleteCollectionParams, Query(...)]
document_params = Annotated[DocumentParams, Query(...)]