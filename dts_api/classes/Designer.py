from typing import Protocol

from lxml import etree
from lxml.etree import ElementTree, Element


class Designer(Protocol):

    @staticmethod
    def design_root(*args, **kwargs):
        ...
    @staticmethod
    def design_subsection(*args, **kwargs):
        ...

class HtmlDesigner:

    @staticmethod
    def design_root(*args, **kwargs):
        dts_resource, fragment, nsmap = args
        if kwargs:
            _, = kwargs

        with open("dts_api/transform/html/xml_to_html.xsl", "r") as xslt_file:

            # parser = etree.XMLParser(remove_comments=True)
            xslt: ElementTree = etree.parse(xslt_file)
            transform = etree.XSLT(xslt)

            html: ElementTree = transform(fragment)
            return html

    @staticmethod
    def design_subsection(*args, **kwargs):
        pass


class XmlDesigner:

    @staticmethod
    def design_root(*args, **kwargs):

        fragment, dts_resource, nsmap = args
        if kwargs:
            _, = kwargs
        resource: Element = fragment.find('TEI', namespaces=nsmap)
        representation: ElementTree = ElementTree(resource)

        return representation

    @staticmethod
    def design_subsection(*args, **kwargs):

        fragment, dts_resource, nsmap = args
        if kwargs:
            _, = kwargs

        with open("dts_api/template/dts_tei_template.xml", "r") as file:

            document: ElementTree = etree.parse(file)
            namespace = list(nsmap.values()).pop()
            header = dts_resource.find('{%s}Document/TEI/teiHeader' % namespace, namespaces=nsmap)

            if len(fragment):
                # todo : add doc

                base = "{%s}wrapper" % "https://w3id.org/dts/api#"
                element: Element = Element(base, nsmap={"dts": "https://w3id.org/dts/api#"})
                for cite_unit in fragment:
                    for xml_el in cite_unit.find("content").iterchildren():
                        element.append(xml_el)

                root_node: Element = document.getroot()
                document_header = document.find('{%s}teiHeader' % namespace, namespaces=nsmap)
                root_node.replace(document_header, header)
                body = document.find('.//body', namespaces={None: namespace})
                body.append(element)
                return document
