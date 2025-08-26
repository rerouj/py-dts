import copy
from pathlib import Path
from urllib.parse import urljoin
from typing import Protocol, Union
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

from lxml import etree
from lxml.etree import ElementTree

from dts_api.classes.Utils import nsmp
from dts_api.model.MetadataModel import IndexMetadataModel


class FileStorage(Protocol):

    def open_document(self, path: Union[str | None] = None) -> str:
        ...
    def save_document(self, path: str):
        ...
    def __str__(self):
        ...

class LocalFileStorage:

    def __init__(self, base_path: str, metadata_path: str):
        self.type = "local"
        self.base_path = base_path  # local document store base path
        self.metadata_path = metadata_path
        self.full_path = Path(self.base_path) / self.metadata_path


    def open_document(self, index: IndexMetadataModel = None) -> str | tuple:
        if index:
            if index.type == "collection":
                raise ValueError("This is a collection, not a document")
            resource_path = Path(self.base_path) / index.location
            try:
                with open(resource_path, "r") as file:

                    prefix, namespace, nsmap = nsmp({'tei': "http://www.tei-c.org/ns/1.0"})
                    # todo : pass parser arg value from config
                    parser = etree.XMLParser(remove_comments=True)
                    tree: ElementTree = etree.parse(file, parser)
                    cite_structure = tree.xpath(f'.//tei:refsDecl', namespaces=nsmap).pop()

                    return copy.deepcopy(tree), index.citation_trees, copy.deepcopy(cite_structure)
            except FileNotFoundError:
                raise FileNotFoundError("[Storage] File not found")
        else:
            md_path = self.full_path
            with open(md_path) as f:
                return f.read()

    def save_document(self, path: str):
        pass

    def __str__(self):
        return f"LocalFileStorage: {self.base_path}"

class GithubFileStorage:

    def __init__(self, base_path: str, metadata_path: str):
        self.type = "local"
        self.base_path = base_path  # local document store base path
        self.metadata_path = metadata_path

    def open_document(self, index: IndexMetadataModel = None) -> str | tuple:
        if index:
            if index.type == "collection":
                raise ValueError("This is a collection, not a document")
            resource_path = urljoin(self.base_path, index.location)
            try:
                file = urlopen(resource_path)
                prefix, namespace, nsmap = nsmp({'tei': "http://www.tei-c.org/ns/1.0"})
                # todo : pass parser arg value from config
                parser = etree.XMLParser(remove_comments=True)
                tree: ElementTree = etree.parse(file, parser)
                cite_structure = tree.xpath(f'.//tei:refsDecl', namespaces=nsmap).pop()

                return copy.deepcopy(tree), index.citation_trees, copy.deepcopy(cite_structure)
            except FileNotFoundError:
                raise FileNotFoundError("[Storage] File not found")
            except URLError:
                raise URLError(reason="[Storage] The Internet connexion has been lost.", filename=resource_path)
        else:
            try:
                md_path = self.metadata_path
                return urlopen(md_path).read()
            except HTTPError:
                # todo
                raise FileNotFoundError('This metadata file is not reachable: please check information provided into the .env file')
            except URLError:
                raise URLError("[Storage] The Internet connexion has been lost.")

    def save_document(self, path: str):
        pass
    def __str__(self):
        return f"GithubFileStorage: {self.base_path}"