from copy import deepcopy
from typing import Protocol
from lxml.etree import Element
from dts_api.classes.Utils import nsmp
from dts_api.classes.Error import BadRangeError
from dts_api.model.NavigationModel import CitableUnit
from dts_api.funcs.common import is_request_out_of_range
from dts_api.funcs.xml_tools import (pick_root, pick_ref, pick_ref_siblings, pick_ref_parent,
                                     narrow_selection as narrower, populate_content)

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
    @staticmethod
    def get_navigation_info(toc, nsmap, ref=None, start=None, end=None):
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
        if start_element is None and end_element:
            raise BadRangeError(f"range error : start({start}) and end({end}) references are not on the same level")
        if start_element and end_element is None:
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

    # todo: make signature match with protocol
    def get_content(self, *args):
        builder: ContentBuilder
        toc, ref, tree, document = args

        fragment = pick_ref(ref, toc, self.nsmap)
        populate_content(fragment, document, self.nsmap)
        return [fragment]

    def get_milestone(*args):
        builder: ContentBuilder
        toc, start, end, document, nsmap = args

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