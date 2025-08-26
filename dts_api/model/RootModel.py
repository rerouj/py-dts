from pydantic import BaseModel, Field

class RootModel(BaseModel):

    context: str = Field(serialization_alias="@context", default="https://distributed-text-services.github.io/specifications/context/1-alpha1.json")
    dts_version: str = Field(serialization_alias="dtsVersion", default="1-alpha")
    id: str = Field(serialization_alias="@id", default="/api/dts/")
    type: str = Field(serialization_alias="@type", default="EntryPoint")
    collection: str = Field(default="/api/dts/collection/{?id,page,nav}")
    navigation: str = Field(default="/api/dts/navigation/{?resource,ref,start,end,down,tree,page}")
    document: str = Field(default="/api/dts/document/{?resource,ref,start,end,tree,mediaType}")