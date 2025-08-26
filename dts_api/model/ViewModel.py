from collections import namedtuple
from typing import Optional, Union
from urllib.parse import urlunparse, urlencode
from pydantic import BaseModel, Field, field_serializer
from dts_api.model.ParameterModel import CollectionParams, NavigationParams


class View(BaseModel):
    id: str = Field(serialization_alias="@id", default="1")
    type: str = Field(default="Pagination")
    first: Optional[str] = Field(default=None)
    previous: Optional[str] = Field(default=None)
    next: Optional[str] = Field(default=None)
    last: Optional[str] = Field(default=None)

class PartialCollectionView(BaseModel):

    """
    Model for the 'view' field (pagination) in Collection
    """

    id: str = Field(serialization_alias="@id", default="")
    type: str = Field(serialization_alias="@type", default="Pagination")
    first: str = ""
    previous: str = ""
    next: str = ""
    last: str = ""
    url_components: "UrlComponent" = Field(exclude=True)

    def model_post_init(self, __context):
        self.set_path(self.url_components)

    def set_path(self, url_components: "UrlComponent"):
        """
        Set url path for each view field, where complete url is needed
        see : https://distributed-text-services.github.io/specifications/versions/unstable/#collection-endpoint
        :param url_components: UrlComponent
        :return:
        """

        model_fields = ['last', 'previous', 'id', 'next', 'first']

        Components = namedtuple(
            typename='Components',
            field_names=['scheme', 'netloc', 'url', 'path', 'query', 'fragment']
        )

        for field in model_fields:
            field_value = getattr(self, field)
            url_components.query.page = field_value
            url = urlunparse(Components(**url_components.model_dump(exclude_none=True)))
            setattr(self, field, url)

class UrlComponent(BaseModel):
    """
    Dataclass for URL components retrieved with Request.url.components
    """
    scheme: str
    netloc: str
    url: str
    query: Union["CollectionParams", "NavigationParams"]
    fragment: str
    path: str = ''

    @field_serializer('query')
    def serialize_query(self, query: CollectionParams, _info) -> str:
        return urlencode(query.model_dump(exclude_none=True, exclude_unset=True))

class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 10
    offset: int = 0
