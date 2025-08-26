from typing import Optional, Any
from pydantic import BaseModel, Field, AliasChoices, model_validator, ConfigDict

from dts_api.classes.Utils import set_path
from dts_api.model.MetadataModel import IndexMetadataModel
from dts_api.model.ViewModel import UrlComponent, View, PartialCollectionView
from dts_api.settings.settings import get_settings

settings = get_settings()

class Doc(BaseModel):
    id: str = Field(serialization_alias="@id")
    title: str = Field(default="My title")

class CollectionBase(BaseModel):

    context: str = Field(serialization_alias="@context", default=f"{settings.dts_context}")
    id: str = Field(serialization_alias="@id", default="1")
    type: str = Field(default="Collection", serialization_alias="@type")
    collection: str = Field(default="{?id,page,nav}")
    dtsVersion: str = Field(default=f"{settings.dts_version}")
    title: str = "My title"
    totalParents: int = 0
    totalChildren: int = 0
    description: str = "My description"
    dublin_core: dict = Field(serialization_alias="dublinCore", default=None)
    extensions: dict = None
    index: Optional["IndexMetadataModel"] = Field(default=None, exclude=True)
    url_components: "UrlComponent" = Field(default=None, exclude=True)

class Collection(CollectionBase):

    # model_config = ConfigDict(serialize_by_alias=True)

    items: list["SubCollection"] | list["SubCollectionResource"] = Field(
        validation_alias=AliasChoices("children", "works", "ti:edition"),
        serialization_alias="member",
        default=None)

    view: PartialCollectionView = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def choose_items_model(cls, values):
        if "type" in values:
            values["children"] = [SubCollection(**item, index=values["index"], url_components=values["url_components"]) if item['type'] == 'collection' else SubCollectionResource(**item, totalChildren=0, index=values["index"], url_components=values["url_components"]) for item in values['children']]  # Use ExtraFieldsAddress
        return values

    def model_post_init(self, __context: Any) -> None:
        self.context = f"{settings.dts_context}"
        self.dtsVersion = f"{settings.dts_version}"
        self.collection = "%s{?id,page,nav}" % self.url_components.url

class SubCollection(CollectionBase):
    dtsVersion: str = Field(default=f"{settings.dts_version}", exclude=True)
    context: str = Field(serialization_alias="@context", default=f"{settings.dts_context}", exclude=True)

    def model_post_init(self, __context: Any) -> None:
        # self.totalParents = self.index.depth + 1
        self.collection = "%s?id=%s{?id,page,nav}" % (self.url_components.url, self.id)

class SubCollectionResource(CollectionBase):
    navigation: str = "pagination"
    document: str = "collection"
    download: str = Field(exclude=True, default=None)
    dtsVersion: str = Field(default=f"{settings.dts_version}", exclude=True)
    context: str = Field(serialization_alias="@context", default=f"{settings.dts_context}", exclude=True)

    def model_post_init(self, __context: Any) -> None:
        # self.totalParents = self.index.depth + 1
        self.navigation = set_path(self.id, 'navigation', self.url_components)
        self.document = set_path(self.id, 'document', self.url_components)
        self.collection = "%s?id=%s{?id,page,nav}" % (self.url_components.url, self.id)

class CollectionResource(CollectionBase):

    navigation: str = "pagination"
    document: str = "collection"
    download: str = Field(exclude=True, default=None)

    items: list["SubCollection"] | list["SubCollectionResource"] = Field(
        validation_alias=AliasChoices("children", "works", "ti:edition"),
        serialization_alias="member",
        default=None)

    view: View = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def choose_items_model(cls, values):
        if "type" in values and 'children' in values:
            values["children"] = [
                SubCollection(
                    **item, index=values["index"],
                    url_components=values["url_components"]) if item['type'] == 'collection' else SubCollectionResource(
                        **item, totalChildren=0, index=values["index"], url_components=values["url_components"]
                ) for item in values['children']]  # Use ExtraFieldsAddress
        return values

    def model_post_init(self, __context: Any) -> None:
        self.navigation = set_path(self.id, 'navigation', self.url_components)
        self.document = set_path(self.id, 'document', self.url_components)
        self.collection = "%s?id=%s{?id,page,nav}" % (self.url_components.url, self.id)


class CollectionResourcePagination(Collection, CollectionResource):

    items: list["SubCollection"] | list["SubCollectionResource"] = Field(
        validation_alias=AliasChoices("children", "works", "ti:edition"),
        serialization_alias="member",
        default=[])

    view: View = Field(default=View())

    def model_post_init(self, __context: Any) -> None:
        self.navigation = set_path(self.id, 'navigation', self.url_components)
        self.document = set_path(self.id, 'document', self.url_components)
        self.collection = "%s?id=%s{?id,page,nav}" % (self.url_components.url, self.id)

    @model_validator(mode="before")
    @classmethod
    def choose_items_model(cls, values):
        if "type" in values:
            values["children"] = [
                SubCollection(**item, index=values["index"], url_components=values["url_components"]) if item['type'] == 'collection' else SubCollectionResource(
                    **item, totalChildren=0, index=values["index"], url_components=values["url_components"]
                ) for item in values['children']]  # Use ExtraFieldsAddress
        return values
