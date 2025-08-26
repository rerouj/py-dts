from copy import deepcopy

from fastapi import HTTPException
from lxml.etree import ElementTree, Element

from dts_api.classes.Utils import nsmp
from dts_api.model.NavigationModel import CitableUnit
from dts_api.funcs.common import get_siblings


def pick_root(down: int, toc: ElementTree) -> list:
    cite_unit: Element
    prefix, namespace, nsmap = nsmp(None, 'tei')
    path = f"./{prefix}:CitableUnit" if down == -1 else f"./{prefix}:CitableUnit[level<={down}]"
    tmp = toc.xpath(path, namespaces={prefix: nsmap[prefix]})
    return tmp


def pick_ref(ref: str, toc: ElementTree, nsmap: dict) -> Element:
    path = f"./*[@ref='{ref}']"
    element: Element = toc.find(path, namespaces=nsmap)
    if element is not None:
        return element
    else:
        raise HTTPException(status_code=404, detail=f"reference error : value '{ref}' does not exist in table of content")


def pick_ref_siblings(element: Element, siblings, level, down=0):
    sibling: Element
    next_element = element.getnext()
    while next_element is not None and next_element.get('level') != level and next_element.get('level') > level:
        siblings.append(next_element)
        return pick_ref_siblings(next_element, siblings, level, down)
    if down == -1:
        return siblings
    else:
        return list(filter(lambda sib: int(sib.get('level')) <= int(level) + 1 + down, siblings))


def pick_ref_parent(ref: str, toc: ElementTree, nsmap: dict):
    element = pick_ref(ref, toc, nsmap)
    parent = element.get('parent')
    if parent:
        return pick_ref(parent, toc, nsmap)
    else:
        return None

def narrow_selection(member: list, start: str, end: str):
    item: CitableUnit
    identifiers = [item.get('ref') for item in member]
    start_index = identifiers.index(start)
    end_index = identifiers.index(end) + 1
    return member[start_index:end_index]

def term_extractor(ref: Element, nsmap):
    terms = []
    citable_elements: Element = ref.findall('.//CitableData', namespaces=nsmap)
    citable: Element
    for citable in citable_elements:
        citable.attrib.update({'value': citable.text})
        term = {
            citable.get('term'): dict(citable.attrib)
        }
        del term[citable.get('term')]['term']
        terms.append(term)

    return terms if len(terms) else None

def populate_content(*args):
    fragment: Element
    document: ElementTree
    fragment, document, nsmap = args
    path = fragment.get('fullpath')
    query_result: Element = document.find(path)
    content: Element = fragment.find('content')

    if not query_result.__len__():
        siblings = get_siblings([], query_result, query_result.tag)
        content.append(deepcopy(query_result))
        for el in siblings:
            content.append(el)
    else:
        content.append(deepcopy(query_result))