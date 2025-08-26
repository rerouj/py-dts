import re

from copy import deepcopy
from lxml.etree import Element, ElementTree, XML
from dts_api.classes.Utils import nsmp


def get_citation_trees(*args):

    document_citation_trees: Element
    metadata: list

    document, metadata, document_citation_trees, tree, nsmap = args
    citation_trees = [
        {
            'name': tree['name'],
            'position': tree['position'],
            'element': document_citation_trees[tree['position']]
        } for tree in metadata
    ]
    return tree, citation_trees, document, nsmap


def select_tree(*args):

    tree_name: str
    citation_trees: list
    tree_name, citation_trees, document, nsmap = args[0]

    # if nsmap is None:
    #     prefix, namespace, nsmap = nsmp(nsmap, 'tei')
    # else:
    #     prefix, namespace, nsmap = nsmp()

    selected_tree = list(filter(lambda tree: tree['name'] == tree_name, citation_trees)).pop()['element']
    # return [element for element in selected_tree.iter("%sciteStructure" % namespace)], document, tree_name
    return selected_tree, document, tree_name


def prepare_path(*args: tuple[Element, ElementTree, str]) -> tuple[list[Element], ElementTree, str]:
    """
    add tei prefix on each match value that can be found in a CiteStructure element

    :param args: output from previous step on the pipeline
    :return: tuple[Element, ElementTree, str]
    """
    prefix, namespace, nsmap = nsmp(prefix='tei')
    selected_tree, document, tree_name = args[0]

    # handle root element

    match: str = selected_tree.get('match')
    nodes = re.split(r'\s?\|\s?', match)

    if len(nodes):
        for ind, node in enumerate(nodes):
            split_match = re.split(r'/{1,2}', node)
            if "" in split_match:
                split_match.remove("")

            path = "/".join(decorate(split_match, prefix))
            nodes[ind] = "//"+path

        selected_tree.set('match', " | ".join(nodes))

    # decorate sub cite_structure element with prefix

    for cite_element in selected_tree.iterdescendants("%sciteStructure" % namespace):
        match: str = cite_element.get('match')
        split_match = re.split('/{1,2}', match)
        if "" in split_match:
            split_match.remove("")

        path = "/".join(decorate(split_match, prefix))
        cite_element.set('match', path)

    # set full path

    item: Element
    for item in selected_tree.iterdescendants("%sciteStructure" % namespace):
        tmp: list
        parent: Element = item.getparent()
        parent_path = parent.get('match')
        if "|" in parent_path:
            path = " | ".join(list(map(lambda x: f"{x}/{item.get('match')}", re.split('\s?\|\s?', parent_path))))
            item.set('match', path)
        else:
            path = f"{parent_path}/{item.get('match')}"
            item.set('match', path)

    return [item for item in selected_tree.iter("%sciteStructure" % namespace)], document, tree_name


def prepare_md_path(*args: tuple[Element, ElementTree, str]):
    tree, document, tree_name = args[0]
    prefix, namespace, nsmap = nsmp(None, 'tei')
    cite_structure = tree[0]
    el_metadata = cite_structure.iter("%sciteData" % namespace)
    for cite_data in el_metadata:
        match = cite_data.get('use')
        split_match = re.split('/{1,2}', match)
        if "" in split_match:
            split_match.remove("")
        path = "/".join(decorate(split_match, prefix))
        cite_data.set('use', path)

    return tree, document, tree_name

def tag_original_document(*args) -> tuple[ElementTree, str, bool]:

    """
    copy and enrich the original document with CiteStructure data
    return a copy of the original xml ElementTree

    :param args: tree: tree selected in the refsDecl element (citationStructure element)
    :param args: document:
    :param args: nsmap:
    :return:
    """

    tree, document, tree_name = args[0]

    prefix, namespace, nsmap = nsmp(None, 'tei')

    while len(tree):

        structure_el: Element = tree.pop(0)
        structure_parent = structure_el.getparent()
        el_metadata = structure_el.findall("%sciteData" % namespace)
        match = structure_el.get('match')

        # set citeStructure level
        parent_level = structure_el.getparent().get('level')
        if parent_level:
            next_level = str(int(parent_level)+1)
            structure_el.set('level', next_level)
        elif parent_level is None and structure_parent.tag == namespace + "refsDecl":
            structure_el.set('level', '1')

        content = document.xpath(match, namespaces=nsmap)

        element: Element

        for ind, element in enumerate(content):

            # build CitableUnit for each element found with citeStructure match value

            citable_unit: Element = Element(f"{namespace}CitableUnit", nsmap=nsmap)
            abstract_path = document.getelementpath(element)

            # set the actual content element with her ref

            if structure_el.get('use') == 'position()':
                res = re.search(r"\[(\d*)]$", abstract_path)
                if res:
                    ref = res.group(1)
                else:
                    ref = "1"
            else:
                ref = element.get(structure_el.get('use')[1:])

            citable_unit.set('ref', ref)
            citable_unit.set('unit', structure_el.get('unit'))
            citable_unit.set('match', match)
            citable_unit.set('delim', structure_el.get('delim') if structure_el.get('delim') else "")
            citable_unit.set('fullpath', abstract_path)
            citable_unit.set('level', structure_el.get('level'))

            element.set('ref', ref)
            element.addprevious(citable_unit)

        # beta version: add citeData (dc-terms) value to TOC

        for el in el_metadata:
            md_content = document.xpath(f"{match}/{el.get('use')}", namespaces=nsmap)
            cite_property = el.get('property')
            if "http://purl.org/dc/elements" in cite_property or "http://purl.org/dc/terms" in cite_property:
                for i in md_content:
                    cite_data: Element = Element(f"{namespace}CitableData", nsmap=nsmap)
                    cite_data.text = i.text
                    # remove all prefixes from attributes keys (not necessarily a good idea...)
                    attrib = {re.split(r'{.*}', k)[-1]: v for k, v in i.attrib.items() if 'http' in k}
                    for a in attrib:
                        cite_data.set(a, attrib[a])
                    dc_term = cite_property.split("/")[-1]
                    cite_data.set('term', dc_term)
                    i.addprevious(cite_data)

        tag_original_document((tree, document, tree_name))

    return document, tree_name, True


def build_toc(*args):

    """
    Build Table of Content (TOC).

    TOCs are simple XML document that represent content of a work as a flat structure
    TOC has CitationStructure and CitableUnit as members.
    CitableUnit can be requested through their attribute
    In CitableUnit are the citable elements of a work. These elements can be retrieved
    and inserted in a DTS fragment representation

    :param args : original_tree: original document
    :param args : copy_tree: enriched document (deepcopy) with CitableUnit element
    :param args : tree_name: allows selecting a concurrent navigation
    :param args : ns: nsmap of the document
    :param args : clean: remove all CitableUnit element and references from CitableUnit main node
    :return: CitationTree object as an ElementTree
    """

    copy_tree: ElementTree
    tree_name: str
    nsmap: object
    clean: bool
    copy_tree, tree_name, clean = args[0]

    prefix, namespace, nsmap = nsmp()

    root: Element = Element('CitationTree', nsmap=nsmap)
    root.set('tree', tree_name)
    toc: ElementTree = ElementTree(root)

    citation_units = copy_tree.findall(f'.//CitableUnit', namespaces=nsmap)
    unit: Element
    for unit in citation_units:
        dc: Element = Element(f'DublinCore', nsmap=nsmap)
        tmp: Element = unit.getnext()
        content: Element = Element(f'content', nsmap=nsmap)
        # catch dc metadata
        dc_items = tmp.findall('%sCitableData' % namespace, namespaces=nsmap)
        if len(dc_items):
            [dc.append(dc_item) for dc_item in dc_items]
        level = Element("level", nsmap=nsmap)
        level.text = unit.get('level')
        unit.append(level)
        unit.append(content)
        unit.append(dc)
        root.append(unit)

    return toc, 1, nsmap


def complete_ref(*args):
    """
    References are built with the match parameter from the citationStructure elements.
    References are incomplete when coming out of the build_toc method,
    They are defined outside of context and independently of parent/child references.

    This method run again through all the citableUnits available in the TOC
    build complete references and add parent reference for each CitableUnit

    :param args : citableunits: list of all CitableUnit elements available in a DtsResource document
    :param args : nsmap: lxml namespace object
    :param args : level: start level
    :return:
    """

    level: int
    nsmap: object
    citationtree: Element

    citationtree, level, nsmap = args[0]

    citable = citationtree.findall(f'CitableUnit[@level="{level}"]', namespaces=nsmap)

    if len(citable):

        unit: Element
        for ind, unit in enumerate(citable):

            children = []

            for nxt in unit.itersiblings():
                if int(nxt.get('level')) == int(unit.get('level')) + 1:
                    children.append(nxt)
                elif int(nxt.get('level')) >= int(unit.get('level')) + 2:
                    pass
                else:
                    break

            child: Element
            for child in children:
                ref = f"{unit.get('ref')}{child.get('delim')}{child.get('ref')}"
                child.set('ref', ref)
                child.set('parent', unit.get('ref'))

        return complete_ref((citationtree, level+1, nsmap))
    else:
        return citationtree

def decorate(paths: list[str], prefix: str) -> list[str]:
    decorated = []
    for path in paths:
        if is_axe(path):
            pattern = r"(.*::)(\w*)"
            path = re.sub(pattern, f"\\1{prefix}:\\2", path)
            decorated.append(path)
        # elif is_param(path):
        #     # todo: log or raise error when a parameter is in the metadata path of a citeData element
        #     decorated.append(path)
        else:
            path = f"{prefix}:{path}"
            decorated.append(path)
    return decorated

def is_axe(path: str) -> bool:
    match = re.search(r"::", path)
    if match:
        return True
    else:
        return False

def is_param(path: str) -> bool:
    match = re.search(r"@", path)
    if match:
        return True
    else:
        return False

def set_dts_resource(namespace: str = 'http://www.tei-c.org/ns/1.0'):

    base = f'<?xml version="1.0"?><DtsResource xmlns="{namespace}">' \
           '<CitationTrees></CitationTrees><TableOfContent></TableOfContent>' \
           '<Document></Document></DtsResource>'

    element: Element = XML(base)
    root: ElementTree = ElementTree(element)

    return root

def get_siblings(siblings: list, element, origin_tag):
    next_element = element.getnext()
    if next_element is not None:
        tag = next_element.tag
        if tag == origin_tag:
            return siblings
        else:
            siblings.append(deepcopy(next_element))
            return get_siblings(siblings, next_element, origin_tag)
    else:
        return siblings

def is_request_out_of_range(start: int, down: int, milestone: list):
    if len(milestone):
        return int(max(list(set(list(map(lambda x: x.get('level'), milestone)))))) - start < down
    else:
        return False