from typing import Protocol, TypeVar, Union

from dts_api.classes.RepresentationBuilder import RepresentationBuilder
from dts_api.classes.Designer import Designer
from dts_api.classes.Utils import nsmp
from dts_api.model.CollectionModel import Collection
from dts_api.model.MetadataModel import IndexMetadataModel
from dts_api.model.ParameterModel import CollectionParams, PostCollectionParams, DeleteCollectionParams

T = TypeVar("T")

class RepresentationFactory(Protocol):

    def __init__(self, request, builder):
        self.request = request
        self.builder = builder

    def build(self, *args, **kwargs):
        ...

class CollectionFactory:

    def __init__(self, builder):
        self.builder: RepresentationBuilder = builder

    def build(self, params: CollectionParams, index: IndexMetadataModel, content: dict):
        self.builder.load_content(index, content, params)
        collection: Collection = self.builder.get_representation()
        self.builder.decorate(index)
        if collection.items and collection.type == 'Resource':
            self.builder.paginate(collection.items, params)
        if collection.type == "collection":
            self.builder.paginate(collection.items, params)
        return self.builder.get_representation()

class NavigationFactory:

    def __init__(self, builder):
        self.builder = builder

    def build(self, *args, **kwargs):
        index, navigation, params = args
        self.builder.load_content(index, navigation)
        navigation = self.builder.get_representation()
        if navigation.member is not None:
            self.builder.paginate(navigation.member, params)
        self.builder.decorate(self.builder.get_representation(), params)
        return self.builder.get_representation()

class DocumentFactory:

    def __init__(self, builder):
        self.builder: Designer = builder
        prefix, namespace, nsmap = nsmp()
        self.nsmap = nsmap
        self.prefix = prefix
        self.namespace = namespace

    def build(self, *args):

        index, document, params = args
        content, dts_resource = document

        if params.ref is None and params.start is None and params.end is None:
            return self.builder.design_root(content, dts_resource, self.nsmap)
        else:
            representation = self.builder.design_subsection(content, dts_resource, self.nsmap)
            return representation