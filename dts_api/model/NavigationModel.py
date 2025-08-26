import dataclasses

from typing import Annotated
from dts_api.model.ViewModel import View
from dts_api.settings.settings import get_settings
from pydantic import BaseModel, Field, model_serializer

settings = get_settings()

class NavigationModel(BaseModel):
    context: str = Field(default=settings.dts_context, serialization_alias="@context")
    dts_version: str = Field(default=settings.dts_version, serialization_alias="@dtsVersion")
    type: str = Field(default="Navigation", serialization_alias="@type")
    id: str = Field(default="Resource", serialization_alias="@id")
    resource: "NavigationResource" = Field(default=None)
    ref: "CitableUnit" = Field(default=None)
    start: "CitableUnit" = Field(default=None)
    end: "CitableUnit" = Field(default=None)
    member: list | None = Field(default=None)
    view: View = Field(default=None)

class NavigationResource(BaseModel):
    id: str = Field(default="Resource", serialization_alias="@id")
    type: str = Field(default="Navigation", serialization_alias="@type")
    collection: str = Field(default="{?id,page,nav}")
    navigation: str = Field(default="{&page,nav}")
    document: str = Field(default="{&ref,down,start,end,tree,page}")
    citation_trees: list["CitationTree"] = Field(default=[])

class CitationTree(BaseModel):
    identifier: str = Field(default=None)
    type: str = Field(default="CitationTree", serialization_alias="@type")
    citeStructure: list["CiteStructure"] = Field(default=None, serialization_alias="citeStructure")
    description: str = Field(default=None)

class CiteStructure(BaseModel):
    type: str = Field(default="CiteStructure", serialization_alias="@type")
    citeType: str = Field(default="CiteStructure", serialization_alias="citeType")
    citeStructure: list = Field(default=None, serialization_alias="citeStructure")

@dataclasses.dataclass
class OmitIfNone:
    pass

class CitableUnit(BaseModel):
    identifier: str = Field(default="identifier")
    type: str = Field(default="CitableUnit", serialization_alias="@type")
    level: int | None
    parent: Annotated[str | None, OmitIfNone()] = Field(default=None)
    cite_type: str = Field(default="cite type", serialization_alias="citeType")
    dublin_core: list | None = Field(default=None, serialization_alias="dublinCore")
    extensions: dict = Field(default=None)

    # include parent field when the value is set to None
    # workaround : https://github.com/pydantic/pydantic/discussions/5461
    @model_serializer
    def _serialize(self, skip=False):
        serialized_model: dict = {}
        if not skip:
            omit_if_none_fields = {
                k
                for k, v in self.__class__.model_fields.items()
                if any(isinstance(m, OmitIfNone) for m in v.metadata)
            }
            # return {k: v for k, v in self if k in omit_if_none_fields or v is not None}
            for k, v in self:
                if k in omit_if_none_fields or v is not None:
                    k = self.__class__.model_fields[k].serialization_alias if self.__class__.model_fields[k].serialization_alias else k
                    serialized_model[k] = v
            return serialized_model
        # else, return serialization by alias
        # for k, v in self:
        #     if self.__class__.model_fields[k].serialization_alias:
        #         tmp[self.__class__.model_fields[k].serialization_alias] = v
        #     else:
        #         tmp[k] = v
        # return tmp
