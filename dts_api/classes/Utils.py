import math
import warnings

from typing import Union, List
from urllib.parse import urlunparse
from collections import deque, namedtuple

from fastapi import HTTPException
from starlette.requests import Request
from dts_api.model.MetadataModel import IndexMetadataModel
from dts_api.model.ParameterModel import CollectionParams, NavigationParams
from dts_api.model.ViewModel import PartialCollectionView, PaginationParams, UrlComponent


def default_index_algorithm(md: dict, sep='.'):

    queue = deque([(md, '')])
    result = []
    id_counter = 1

    while queue:
        current, path = queue.popleft()
        if isinstance(current, list):
            for index, item in enumerate(current):
                new_path = f"{path}{sep}{index}" if path else str(index)
                queue.append((item, new_path))
        elif isinstance(current, dict):
            for key, value in current.items():
                new_path = f"{path}{sep}{key}" if path else key
                if key == 'id':
                    children_count: int = 0
                    if 'children' in current:
                        children_count = len(current['children'])
                    payload = {
                        'id': value,
                        'type': current['type'],
                        'children_count': children_count,
                        'path': new_path,
                        'location': current.get('location', None),
                        'citation_trees': current.get('CitationTrees', None),
                    }
                    result.append(IndexMetadataModel(**payload))
                    id_counter += 1
                if isinstance(value, (dict, list)):
                    queue.append((value, new_path))
    return result


def pta_index_algorithm(md: dict, sep='.'):

    # this is a legacy piece of code, needs refactoring

    queue = deque([(md, '')])
    result = []

    while queue:
        current, path = queue.popleft()
        if isinstance(current, list):
            for index, item in enumerate(current):
                new_path = f"{path}{sep}{index}" if path else str(index)
                queue.append((item, new_path))
        elif isinstance(current, dict):
            for key, value in current.items():
                new_path = f"{path}{sep}{key}" if path else key
                if key == 'textgroup':
                    result.append(
                        {'id': value['ti:textgroup']['@urn'], 'path': new_path}
                    )
                if key == 'ti:work':
                    result.append({'id': value['@urn'], 'path': new_path})
                    queue.append((value, new_path))
                if key == '@urn':  # on ti:edition
                    if 'ti:label' not in current:
                        result.append({'id': value, 'path': new_path})
                if key == 'ti:label':
                    result.append({'id': current['@urn'], 'path': new_path})
                if key == 'works' or key == 'ti:edition':
                    if isinstance(value, list):
                        queue.append((value, new_path))
                    else:
                        location = '/'.join([*value['@workUrn'][12:].split('.'), f'{value["@urn"][12:]}.xml'])
                        result.append({'id': value['@workUrn'], 'location': location, 'path': new_path, 'type': 'Resource'})
    return [IndexMetadataModel(**index) for index in result]

def collection_paginator(
        url_components: list,
        model: type[PartialCollectionView],
        members: [Union[str | None]] = List[None],
        params: PaginationParams = 0
) -> tuple[type[list], PartialCollectionView]:

    if params.limit == 0:
        params.limit += 10
    if not members:
        members = []
    members_len = len(members) if len(members)-params.offset < 0 else len(members)-params.offset
    remaining = members_len % params.limit
    pages = math.ceil((members_len - remaining) / params.limit)

    # if params.page > pages + 1 or params.page <= 0:
    #     raise HTTPException(status_code=404, detail="Page value out of range")

    if remaining:
        pages += 1

    page_selected = params.page if params.page > 0 else 1
    first_page = 1
    previous_page = page_selected-1 if params.page > 1 else 1
    next_page = page_selected+1 if page_selected < pages else page_selected

    base_sigma: int
    sigma: int

    page_sigma = params.limit**2*(page_selected-1)
    start = int(page_sigma / params.limit)
    end = start + params.limit if params.page < pages else None

    paginated_member_array = members[start:end]
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
        partial_view = model(
            id=str(params.page),
            first=str(first_page),
            previous=str(previous_page),
            next=str(next_page),
            last=str(pages),
            url_components=url_components
        )

    return paginated_member_array, partial_view

def get_url_components(request: Request, params_model: CollectionParams | NavigationParams) -> UrlComponent:
    component_schema = ['scheme', 'netloc', 'url', 'path', 'query', 'fragment']
    tmp_component = [
        request.url.components.scheme,
        request.url.components.netloc,
        request.url.components.path,
        '',  # Request.url.path signature does not match urllib unparse component signature
        params_model,
        request.url.components.fragment
    ]
    return UrlComponent(**dict(zip(component_schema, tmp_component)))

def set_path(resource_id: str, field: str, url_components: UrlComponent):
    """
    Set url path for each view field, where complete url is needed
    see : https://distributed-text-services.github.io/specifications/versions/unstable/#collection-endpoint
    :param resource_id: resource id that will be used in the url
    :param field: route name that will be used in the query
    :param url_components: UrlComponent
    :return:
    """

    Components = namedtuple(
        typename='Components',
        field_names=['scheme', 'netloc', 'url', 'path', 'query', 'fragment']
    )
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
        components_dump = url_components.model_dump()

    url = url_components.url.split('/')
    url[-1] = "%s/" % field
    components_dump["url"] = '/'.join(url)
    components_dump["query"] = components_dump["query"].split("&")[0] # remove all extra query params

    if field == 'collection':
        components_dump["query"] = 'resource=%s{&ref,start,end,tree,mediaType}' % resource_id
    elif field == 'navigation':
        components_dump["query"] = 'resource=%s{&page,nav}' % resource_id
    elif field == 'document':
        components_dump["query"] = 'resource=%s{&ref,down,start,end,tree,mediaType}' % resource_id
    return urlunparse(Components(**components_dump))

def nsmp(nsmap=None, prefix=None):
    if nsmap is None:
        if prefix is not None:
            nsmap = {prefix: 'http://www.tei-c.org/ns/1.0'}
        else:
            nsmap = {None: 'http://www.tei-c.org/ns/1.0'}
    else:
        if prefix is not None:
            nsmap = {prefix: nsmap[nsmap.keys()[0]]}

    prefix = list(nsmap.keys()).pop()
    namespace = "{%s}" % nsmap[prefix]
    return prefix, namespace, nsmap