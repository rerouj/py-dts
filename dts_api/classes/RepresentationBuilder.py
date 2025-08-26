from copy import deepcopy
from typing import Protocol, TypeVar, Union, Callable, Type

from dts_api.classes.Error import BadRangeError
from dts_api.funcs.common import is_request_out_of_range
from dts_api.model.NavigationModel import CitableUnit, NavigationModel, NavigationResource, CitationTree
from dts_api.funcs.xml_tools import (pick_root, pick_ref, pick_ref_siblings, pick_ref_parent,
                                     narrow_selection as narrower, term_extractor, populate_content)

from lxml.etree import Element
from starlette.requests import Request

from dts_api.classes.Store import Store
from dts_api.classes.Utils import get_url_components, set_path, nsmp
from dts_api.model.CollectionModel import Collection, CollectionResource
from dts_api.model.MetadataModel import IndexMetadataModel
from dts_api.model.ParameterModel import CollectionParams, NavigationParams
from dts_api.model.ViewModel import PartialCollectionView, PaginationParams, UrlComponent

T = TypeVar("T")
params_type = Union[CollectionParams]

class RepresentationBuilder(Protocol):

    def reset(self):
        ...
    def get_representation(self):
        ...
    def load_content(self, *args, **kwargs):
        ...
    def paginate(self, *args, **kwargs) -> T:
        ...
    def decorate(self, *args, **kwargs) -> T:
        ...

class CollectionBuilder:

    __content: dict

    def __init__(self, request: Request, paginator: Callable, store: Store):
        self.request: Request = request
        self.collection: Type[Collection] = Collection
        self.collection_resource: Type[CollectionResource] = CollectionResource
        self.model: Collection | CollectionResource | None = None
        self.paginator = paginator
        self.view = PartialCollectionView
        self.store = store

    def reset(self):
        ...

    def get_representation(self):
        return self.model

    def load_content(self, *args, **kwargs):
        """
        Init model with content
        :return: self.model
        """
        index: IndexMetadataModel
        content: dict
        index, content, params = args
        if kwargs:
            _, = kwargs

        url_components: UrlComponent = get_url_components(self.request, params)

        if content.get('type') == 'collection':
            self.model = self.collection(**content, index=index, url_components=url_components)
        else:
            if 'children' in content:
                self.model = self.collection_resource(**content, index=index, url_components=url_components)
            else:
                self.model = self.collection_resource(**content, index=index, url_components=url_components)

    def paginate(self, *args, **kwargs):
        members, params = args
        if kwargs:
            _, = kwargs

        # preparing url components for pagination model
        url_components: UrlComponent = get_url_components(self.request, params)
        paginated_member_array, partial_view = self.paginator(url_components, self.view, members, PaginationParams(page=params.page, limit=params.limit, offset=params.offset))

        # set paginated items and view
        self.model.items = paginated_member_array
        self.model.view = partial_view

    def decorate(self, *args, **kwargs):
        index: IndexMetadataModel
        if kwargs:
            _, = kwargs
        if args:
            _, = args
        self.model.totalParents = self.store.get_index_count(self.model.id)
        if self.model.type == 'collection':
            self.model.totalChildren = self.store.get_index_children_count(self.model.id)
            for item in self.model.items:
                item.totalParents = self.store.get_index_count(item.id)
                item.totalChildren = self.store.get_index_children_count(item.id)
        else:
            self.model.totalChildren = 0


class NavigationBuilder:
    def __init__(self, request, paginator, store):
        self.request = request
        self.paginator = paginator
        self.representation_model: Type[NavigationModel] = NavigationModel
        self.navigation: NavigationModel | None = None
        self.view = PartialCollectionView
        self. store = store

    def reset(self):
        self.navigation = None

    def get_representation(self):
        return self.navigation

    def load_content(self, *args, **kwargs):

        index: IndexMetadataModel
        content: list
        navigation_info: tuple
        citation_trees: list
        index, content = args
        if kwargs:
            _, = kwargs
        navigation, navigation_info, citation_trees, max_cite_depth = content
        prefix, namespace, nsmap = nsmp()

        member = None
        if navigation is not None:
            member = [
                CitableUnit(
                    type='CitableUnit',
                    identifier=cite_unit.get('ref'),
                    level=cite_unit.get('level'),
                    parent=cite_unit.get('parent'),
                    cite_type=cite_unit.get('unit'),
                    dublin_core = term_extractor(cite_unit, nsmap) if cite_unit is not None else None
                ) for cite_unit in navigation
            ] if len(navigation) else []

        ref, start, end = navigation_info

        if ref is not None:
            ref = CitableUnit(
                type="CitableUnit",
                identifier=ref.get('ref'),
                level=ref.get('level'),
                parent=ref.get('parent'),
                cite_type=ref.get('unit'),
                dublin_core=term_extractor(ref, nsmap) if ref is not None else None
            )
            if member is not None and len(member) and ref not in member:
                member.insert(0, ref)
            self.navigation = self.representation_model(
                id=index.id,
                ref=ref,
                resource=NavigationResource(**{
                    "@type": "Resource",
                    "citation_trees": [CitationTree(**tree) for tree in citation_trees]
                }), member=member
            )

        elif start is not None and end is not None:
            start = CitableUnit(
                type="CitableUnit",
                identifier=start.get('ref'),
                level=start.get('level'),
                parent=start.get('parent'),
                cite_type=start.get('unit'),
                dublin_core=term_extractor(start, nsmap) if start is not None else None
            )
            end = CitableUnit(
                type="CitableUnit",
                identifier=end.get('ref'),
                level=end.get('level'),
                parent=end.get('parent'),
                cite_type=end.get('unit'),
                dublin_core = term_extractor(end, nsmap) if end is not None else None
            )
            self.navigation = self.representation_model(
                id = index.id,
                start=start,
                end=end,
                resource=NavigationResource(**{
                    "@type": "Resource",
                    "citation_trees": [CitationTree(**tree) for tree in citation_trees]
                }),
                member=member
            )
        else:
            self.navigation = self.representation_model(
                id=index.id,
                resource=NavigationResource(**{
                "@type": "Resource",
                "citation_trees": [CitationTree(**tree) for tree in citation_trees]
            }), member=member)

    def paginate(self, *args, **kwargs) -> T:
        params: NavigationParams | CollectionParams
        members, params = args
        if kwargs:
            _, = kwargs

        # preparing url components for pagination model
        url_components: UrlComponent = get_url_components(self.request, params)
        paginated_member_array, partial_view = self.paginator(url_components, self.view, members, PaginationParams(page=params.page, limit=params.limit, offset=params.offset))

        # set paginated items and view
        # todo: harmonizing model field names with Collection model
        self.navigation.member = paginated_member_array if len(paginated_member_array) else []
        self.navigation.view = partial_view

    def decorate(self, *args, **kwargs) -> T:
        representation, params, = args
        if kwargs:
            _, = kwargs

        url_components: UrlComponent = get_url_components(self.request, params)

        representation.resource.collection = set_path(representation.id, 'collection', url_components)
        representation.resource.navigation = set_path(representation.id, 'navigation', url_components)
        representation.resource.document = set_path(representation.id, 'document', url_components)


class ContentBuilder(Protocol):

    @staticmethod
    def get_citation_trees(citation_trees: Element) -> tuple[list, int]:
        ...
    @staticmethod
    def get_root(down, toc, nsmap):
        ...
    @staticmethod
    def get_content(ref, down, toc, nsmap):
        ...
    @staticmethod
    def get_milestone(*args, **kwargs):
        ...
    def get_navigation_info(self, toc, nsmap, ref=None, start=None, end=None):
        ...
    def get_navigation(self):
        ...

class NavigationContentBuilder:

    def __init__(self):
        self.navigation = None

    @staticmethod
    def get_citation_trees(citation_trees: Element) -> tuple[list, int]:
        """
        define citationTrees content from the citation_trees objects in a xml document

        :param citation_trees: citation_trees object from metadata, containing one or multiple citeStructure root elements
        :return: list
        """

        item: Element
        deployed_citation_trees: list = []
        max_cite_depth = []
        for tree in citation_trees:
            count = 0
            tmp = [{"@type": "CiteStructure", "citeType": structure.get('unit'),
                    "parent": structure.getparent().get('unit')} for structure in
                   tree['element'].iter('{http://www.tei-c.org/ns/1.0}citeStructure')]

            while len(tmp) > 1:
                count += 1
                child = tmp.pop()
                for item in tmp:
                    if child['parent'] == item['citeType']:
                        if 'citeStructure' in item.keys():
                            cpy = deepcopy(child)
                            del cpy['parent']
                            item['citeStructure'].append(cpy)
                        else:
                            cpy = deepcopy(child)
                            del cpy['parent']
                            item['citeStructure'] = [cpy]
            max_cite_depth.append(count)
            for item in tmp:
                del item['parent']
            identifier = {'identifier': tree['name']}
            tmp[0] = {
                "@type": "CitationTree",
                "maxCiteDepth": count + 1,
                "citeStructure": [{**identifier, **tmp[0]}]
            }
            deployed_citation_trees.append(tmp.pop())
        if len(deployed_citation_trees) == 1:
            del deployed_citation_trees[0]['citeStructure'][0]['identifier']

        return deployed_citation_trees, max(max_cite_depth) + 1

    @staticmethod
    def get_root(down, toc):
        return pick_root(int(down), toc)

    @staticmethod
    def get_content(ref, down, toc, nsmap):
        # todo : insert here strategy pattern for selecting sort & search algorithms
        siblings: list = []
        element: Element
        if int(down) == 0:
            element = pick_ref_parent(ref, toc, nsmap)
            if element:
                siblings: list = pick_ref_siblings(element, [], element.get('level'))
            else:
                return pick_root(1, toc)

        elif int(down) >= 1:
            element = pick_ref(ref, toc, nsmap)
            siblings: list = pick_ref_siblings(element, [], element.get('level'), int(down) - 1)

        elif int(down) == -1:
            element = pick_ref(ref, toc, nsmap)
            siblings: list = pick_ref_siblings(element, [], element.get('level'), int(down))

        element = pick_ref(ref, toc, nsmap)
        if is_request_out_of_range(int(element.get('level')), int(down), siblings):
            return []
        return siblings
    @staticmethod
    def get_milestone(*args, **kwargs):

        start, end, down, toc, document, nsmap = args
        if kwargs:
            _, = kwargs

        start_element: Element = pick_ref_parent(start, toc, nsmap)
        end_element: Element = pick_ref_parent(end, toc, nsmap)
        if start_element is None and end_element is not None:
            raise BadRangeError(f"range error : start({start}) and end({end}) references are not on the same level")
        if start_element is not None and end_element is None:
            raise BadRangeError(f"range error : start({start}) and end({end}) references are not on the same level")

        if start_element is None and end_element is None:

            start_element = pick_ref(start, toc, nsmap)
            end_element = pick_ref(end, toc, nsmap)

            if start_element.get('level') == end_element.get('level'):
                tmp = pick_root(1, toc)
                narrow_selection = narrower(tmp, start, end)
                item: CitableUnit | Element
                milestone = []
                for item in narrow_selection:
                    element = pick_ref(item.get('ref'), toc, nsmap)
                    siblings = pick_ref_siblings(element, [], element.get('level'),
                                                         int(down) - 1 if int(down) > 0 else -1)
                    siblings.insert(0, item)
                    milestone = milestone + siblings
                if is_request_out_of_range(int(start_element.get('level')), down, milestone):
                    return []
                return milestone

        elif start_element.get('level') == end_element.get('level'):

            parent_element = pick_ref_parent(start, toc, nsmap)
            siblings: list = pick_ref_siblings(parent_element, [], parent_element.get('level'))
            narrow_selection = narrower(siblings, start, end)
            item: Element
            milestone = []
            for item in narrow_selection:
                siblings = pick_ref_siblings(item, [], item.get('level'),
                                                     int(down) - 1 if int(down) > 0 else -1)
                siblings.insert(0, item)
                milestone = milestone + siblings
            if is_request_out_of_range(int(siblings[0].get('level')), down, milestone):
                return []
            return milestone

        raise BadRangeError("")

    @staticmethod
    def get_navigation_info(toc, nsmap, ref=None, start=None, end=None):

        if start and end:
            start_element = pick_ref(start, toc, nsmap)
            end_element = pick_ref(end, toc, nsmap)
            return [None, start_element, end_element]
        else:
            return [pick_ref(ref, toc, nsmap), None, None]

    def get_navigation(self):
        return self.navigation

class DocumentContentBuilder:

    def __init__(self):
        self.document = None
        prefix, namespace, nsmap = nsmp()
        self.prefix = prefix
        self.namespace = namespace
        self.nsmap = nsmap

    def get_citation_trees(self, citation_trees: Element) -> tuple[list, int]:
        ...

    def get_root(self, dts_resource):
        return dts_resource.find('Document', namespaces=self.nsmap)

    def get_content(self, *args):
        builder: ContentBuilder
        toc, ref, tree, document = args

        fragment = pick_ref(ref, toc, self.nsmap)
        populate_content(fragment, document, self.nsmap)
        return [fragment]
    @staticmethod
    def get_milestone(*args, **kwargs):
        builder: ContentBuilder
        toc, start, end, document, nsmap = args
        if kwargs:
            _, = kwargs

        start_element: Element = pick_ref_parent(start, toc, nsmap)
        end_element: Element = pick_ref_parent(end, toc, nsmap)

        if start_element is None and end_element is None:

            start_element = pick_ref(start, toc, nsmap)
            end_element = pick_ref(start, toc, nsmap)

            if start_element.get('level') == end_element.get('level'):
                tmp = pick_root(1, toc)
                narrow_selection = narrower(tmp, start, end)
                item: Element
                for item in narrow_selection:
                    populate_content(item, document, nsmap)
                return narrow_selection

        elif start_element.get('level') == end_element.get('level'):

            parent_element = pick_ref_parent(start, toc, nsmap)
            siblings: list = pick_ref_siblings(parent_element, [], parent_element.get('level'))
            narrow_selection = narrower(siblings, start, end)
            item: Element
            for item in narrow_selection:
                populate_content(item, document, nsmap)
            return narrow_selection

        elif start_element.get('level') != end_element.get('level'):
            raise BadRangeError(f"range error : ref '{start}' (level {start_element.get('level')}) and ref '{end}' (level {end_element.get('level')}) references are not on the same level")

    def get_navigation_info(self, toc, nsmap, ref=None, start=None, end=None):
        ...

    def get_navigation(self):
        ...