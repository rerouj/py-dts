from pathlib import Path
from typing import Protocol
from urllib.request import urlopen
from contextlib import contextmanager


class Database(Protocol):

    def get_metadata(self):
        ...

    @staticmethod
    def get_document():
        ...

class LocalDatabase:

    """returns a local database session and provides basic database operations"""

    def __init__(self, base_path: str, metadata_path: str):

        self.base_path = base_path  # local document store base path
        self.metadata_path = metadata_path
        self.full_path = Path(self.base_path) / self.metadata_path

    @contextmanager
    def get_metadata(self):
        """get metadata file from a local filesystem"""
        try:
            yield open(self.full_path, 'r')
        except:
            raise
        finally:
            pass
    @staticmethod
    def get_document(collection_id: str, doc_ns: str = "http://www.tei-c.org/ns/1.0"):
        """get root element from a xml document stored in the filesystem"""
        print(collection_id, doc_ns)
        """
        for item in self.document_store['collections']:
            if item['id'] == collection_id:
                doc_path = item['location']
                document_location = Path(self.basepath, doc_path)

                with open(document_location, "r") as file:
                    ns = {"tei": doc_ns}
                    # todo : pass parser arg value from config
                    parser = etree.XMLParser(remove_comments=True)
                    tree: _ElementTree = etree.parse(file, parser)

                    if len(item['CitationTrees']):
                        cite_metadata = item['CitationTrees']
                    else:
                        cite_metadata = None

                    cite_structure = tree.xpath(f'.//tei:refsDecl', namespaces=ns).pop()
                    return copy.deepcopy(tree), cite_metadata, copy.deepcopy(cite_structure)

        raise KeyError("document error: this document does not exist in the database")
        """
        pass


class ExistDatabase:

    def __init__(self, base_path, fs_type, credentials):
        self.base_path = base_path
        self.fs_type = fs_type
        self.credentials = credentials

    def get_metadata(self):
        print(self.base_path)
        return {}

    @staticmethod
    def get_document():
        print("get document")
        return {}

class GithubDatabase:

    def __init__(self, base_path: str, metadata_path: str):

        self.base_path = base_path  # local document store base path
        self.metadata_path = metadata_path
        self.full_path = f"{self.base_path}/{self.metadata_path}"

    @contextmanager
    def get_metadata(self):
        print("get metadata")
        yield urlopen(self.full_path)

    @staticmethod
    def get_document():
        print("get document")
        return {}