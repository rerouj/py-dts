from typing import Annotated

from fastapi import Request, Depends

from dts_api.classes import Database
from dts_api.service.services import *
from dts_api.classes.Store import Store
from dts_api.classes.Indexer import DefaultIndexer
from dts_api.deps.settings import settings as main_settings
from dts_api.classes.Designer import XmlDesigner, HtmlDesigner
from dts_api.classes.Database import LocalDatabase, GithubDatabase
from dts_api.classes.FileStorage import LocalFileStorage, GithubFileStorage
from dts_api.classes.Adapter import JsonAdapter, DefaultIngestor, DefaultExtractor
from dts_api.classes.Utils import default_index_algorithm, collection_paginator, nsmp
from dts_api.classes.RepresentationBuilder import CollectionBuilder, NavigationBuilder
from dts_api.classes.Factory import CollectionFactory, NavigationFactory, DocumentFactory
from dts_api.classes.StoreKeeper import CollectionStoreKeeper, NavigationStoreKeeper, DocumentStoreKeeper
from dts_api.classes.ContentExtractor import JsonContentExtractor, NavigationContentExtractor, \
    DocumentContentExtractor

def service_selector(factory: "factory_selector", storekeeper: "storekeeper_selector", actual_route: "requested_route"):

    services = {
        'collection': CollectionService,
        'navigation': NavigationService,
        'document': DocumentService
    }
    return services[actual_route](factory, storekeeper)

def storekeeper_selector(store: "store_dep", content_extractor: "extractor_selector", indexer: "default_indexer", settings: main_settings, actual_route: "requested_route"):
    store_keeper = {
        'collection': CollectionStoreKeeper,
        'navigation': NavigationStoreKeeper,
        'document': DocumentStoreKeeper,
    }
    return store_keeper[actual_route](store, content_extractor, indexer, settings)

def default_indexer(fs: "selected_fs", adapter: "default_adapter"):
    default_algorithm = default_index_algorithm
    return DefaultIndexer(default_algorithm, fs, adapter)

def store_dep():
    store = Store()
    return store

def selected_fs(settings: main_settings):
    match settings.storage:
        case "local":
            return LocalFileStorage(settings.base_path, settings.metadata_path)
        case "github":
            return GithubFileStorage(settings.base_path, settings.metadata_path)

def default_adapter():
    default_ingestor = DefaultIngestor()
    default_extractor = DefaultExtractor()
    JsonAdapter(default_ingestor, default_extractor)

def extractor_selector(actual_route: "requested_route"):

    extractors = {
        'collection': JsonContentExtractor,
        'navigation': NavigationContentExtractor,
        'document': DocumentContentExtractor,
    }
    extractor = extractors[actual_route]
    prefix, namespace, nsmap = nsmp()
    return extractor(prefix, namespace, nsmap)

def factory_selector(builder: "builder_selector", actual_route: "requested_route"):

    factories = {
        'collection': CollectionFactory,
        'navigation': NavigationFactory,
        'document': DocumentFactory
    }
    factory = factories[actual_route]
    return factory(builder)

def builder_selector(request: Request, store: "store_dep", paginator: "paginator_selector", actual_route: "requested_route", designer: "designer_selector"):

    builders = {
        'collection': CollectionBuilder,
        'navigation': NavigationBuilder,
        'document': designer
    }
    builder = builders[actual_route]
    if actual_route != 'document':
        return builder(request, paginator, store)
    else:
        return builder()

def designer_selector(request: Request):

    designers = {
        'text/xml': XmlDesigner,
        'text/html': HtmlDesigner,
        #'json': JsonDesigner
    }

    media_type = request.query_params.get('media_type')

    if media_type is not None and media_type in designers.keys():
        designer = designers[request.query_params.get('media_type')]
        return designer
    elif media_type is None:
        return XmlDesigner
    raise HTTPException(400, "media type error : this media type is not available")

def database_selector(settings: main_settings) -> Database:

    storage = settings.storage

    match storage:
        case "local":
            return LocalDatabase(settings.base_path, settings.metadata_path)
        case "github":
            return GithubDatabase(settings.base_path, settings.metadata_path)

def route(request: Request):
    return request.scope['route'].tags[-1]

def paginator_selector(actual_route: "requested_route"):
    paginator = {
        'collection': collection_paginator,
        'navigation': collection_paginator,
        'document': collection_paginator
    }
    return paginator[actual_route]

service_selector = Annotated[service_selector, Depends()]
factory_selector = Annotated[factory_selector, Depends()]
database_selector = Annotated[database_selector, Depends()]
builder_selector = Annotated[builder_selector, Depends()]
storekeeper_selector = Annotated[storekeeper_selector, Depends()]
store_dep = Annotated[store_dep, Depends()]
extractor_selector = Annotated[extractor_selector, Depends()]
selected_fs = Annotated[selected_fs, Depends()]
default_adapter = Annotated[default_adapter, Depends()]
default_indexer = Annotated[default_indexer, Depends()]
requested_route = Annotated[route, Depends()]
paginator_selector = Annotated[paginator_selector, Depends()]
designer_selector = Annotated[designer_selector, Depends()]