from typing import Union

from lxml.etree import Element
from websockets import Protocol

from dts_api.classes.Cache import Cache
from dts_api.classes.ContentExtractor import ContentExtractor, JsonContentExtractor
from dts_api.classes.DtsResource import DtsResource
from dts_api.classes.Error import CollectionNotFoundError, ResourceNotFoundError
from dts_api.classes.Indexer import Indexer
from dts_api.classes.Pipeline import TocPipelineBuilder
from dts_api.classes.Store import Store
from dts_api.classes.Utils import nsmp
from dts_api.errors.CustomError import MetadataValidationError
from dts_api.model.MetadataModel import IndexMetadataModel
from dts_api.model.ParameterModel import CollectionParams, PostCollectionParams, DeleteCollectionParams
from dts_api.funcs.common import set_citation_trees

collection_params = Union[CollectionParams | PostCollectionParams | DeleteCollectionParams]

class StoreKeeper(Protocol):
    def get_content(self, params: collection_params):
        ...

class CommonStoreKeeper:

    def __init__(self, store, content_extractor: ContentExtractor, indexer: Indexer, settings):
        self.store: Store = store
        self.metadata_extractor: ContentExtractor = JsonContentExtractor()
        self.content_extractor: ContentExtractor = content_extractor
        self.indexer = indexer
        self.settings = settings
        prefix, namespace, nsmap = nsmp()
        self.nsmap = nsmap
        self.prefix = prefix
        self.namespace = namespace
        self.dts_resource = DtsResource(self.namespace, self.nsmap)
        self.pipeline = TocPipelineBuilder().get_pipeline()
        self.cache: Cache = Cache()

    def get_content(self, params: collection_params):

        index_entries: list[IndexMetadataModel] = self.store.get_index_entry(params.resource)

        if not len(index_entries):
            raise ResourceNotFoundError(None)

        item = index_entries.pop()
        if item.type == 'collection':
            raise ResourceNotFoundError("this resource is a collection")

        if not self.cache.get(item.id) or self.cache.get(item.id)[4] != params.tree:
            document, cite_metadata, cite_structure = self.store.get_document(item)
            args = [*self.store.get_document(item), params.tree, self.nsmap]

            # todo: move this to chain of responsibility pattern
            toc: Element = self.pipeline(*args)
            self.cache.set(item.id, (toc, document, cite_metadata, cite_structure, params.tree))
        else:
            toc, document, cite_metadata, cite_structure, last_selected_tree = self.cache.get(item.id)

        # todo: move this inside the store.get_document method
        citation_trees = set_citation_trees(None, cite_metadata, cite_structure, params.tree, None)[1]

        self.dts_resource.set_dts_resource(params.resource, self.namespace, self.nsmap, document, cite_structure, toc)

        payload = {
            **params.model_dump(),
            "dts_resource": self.dts_resource.dts_resource,
            "cite_structure": citation_trees, "document": document
        }
        # return navigation, navigation_info, citation_trees, max_cite_depth
        return item, self.content_extractor.extract_content(**payload)

class CollectionStoreKeeper(CommonStoreKeeper) :

    def get_content(self, params: collection_params):

        collection_id = self.settings.root_collection if params.id is None else params.id
        index_entries: list[IndexMetadataModel] = self.store.get_index_entry(collection_id)

        if not len(index_entries) and params.id is None:
            raise CollectionNotFoundError("Collection not found: please check the ROOT_COLLECTION value in the config file")
        elif not len(index_entries) and params.id is not None:
            raise CollectionNotFoundError(f"Collection '{params.id}' not found")

        main_entry = index_entries[0]

        cache_id: str = '-'.join(str(key) + str(value) for key, value in params.model_dump().items())
        if not self.cache.get(cache_id):
            md = self.store.get_document()
            self.cache.set(cache_id, md)
        else:
            md = self.cache.get(cache_id)

        path: str
        content: dict

        if params.nav == 'parents' and main_entry.depth:
            main_content = self.metadata_extractor.extract_content(md, main_entry.path)
            main_content['children'] = [self.metadata_extractor.extract_content(md, entry.parent) for entry in index_entries]
            content = main_content
        elif params.nav == 'parents' and not main_entry.depth:
            main_content = self.metadata_extractor.extract_content(md, main_entry.path)
            main_content['children'] = []
            content = main_content
        else:
            path = main_entry.path
            content = self.metadata_extractor.extract_content(md, path)
            if "children" in content:
                children = [child for child in content["children"] if child.get('type', '').lower() == 'resource']
                for i, child in enumerate(children):
                    child_md: IndexMetadataModel = self.store.get_index_entry(child['id'])[0]
                    if child_md.citation_trees:
                        tree, citation_tree, cite_structure = self.store.get_document(child_md)
                        tmp_citation_trees = set_citation_trees(None, citation_tree, cite_structure, None, None)[1]
                        citation_trees, max_cite_depth = self.content_extractor.extract_content(structure=tmp_citation_trees)
                        content['children'][i]['CitationTrees'] = citation_trees
                    else:
                        raise MetadataValidationError(errors=[{
                            'type': 'MetadataValidationError',
                            'loc': [content['id'], child['id'], 'citation_trees'],
                            'msg': f"Resource with id '{child['id']}' is "
                                   f"missing citation tree information "
                                   f"in the index metadata. Please provide"
                                   f" the basic CitationTree : {{"
                                   f"'name': 'default'"
                                   f"'position': 0"
                                   f"}}"
                        }])

        return main_entry, content

class NavigationStoreKeeper(CommonStoreKeeper):
    ...
class DocumentStoreKeeper(CommonStoreKeeper):
    ...
