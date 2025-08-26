from threading import Lock
from typing import TypeVar

from dts_api.classes.Adapter import JsonAdapter, DefaultIngestor, DefaultExtractor, Adapter
from dts_api.classes.FileStorage import FileStorage, LocalFileStorage, GithubFileStorage
from dts_api.classes.Indexer import DefaultIndexer
from dts_api.classes.Utils import default_index_algorithm, pta_index_algorithm
from dts_api.model.MetadataModel import IndexMetadataModel
from dts_api.settings.settings import get_settings

T = TypeVar('T')

class StoreMeta(type):

    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(StoreMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


    def get_document(self, *args, **kwargs) -> T:
        ...
    def get_index_entry(self, *args, **kwargs):
        ...
    def get_index_count(self, *args, **kwargs):
        ...
    def get_index_children_count(self, *args, **kwargs):
        ...
    def attach_adapter(self, adapter):
        ...
    def attach_fs(self, fs):
        ...


class Store(metaclass=StoreMeta):

    _instance = None  # Class variable to store the singleton instance

    def __init__(self, adapter: Adapter = None):
        print("Store initialized")
        if not hasattr(self, 'initialized'):

            self.settings = get_settings()

            if adapter is None:
                self.md_adapter = JsonAdapter(DefaultIngestor(), DefaultExtractor())
            else:
                self.md_adapter = adapter

            match self.settings.storage:
                case 'local':
                    self.fs: FileStorage = LocalFileStorage(self.settings.base_path, self.settings.metadata_path)
                case 'github':
                    self.fs: FileStorage = GithubFileStorage(self.settings.base_path, self.settings.metadata_path)

            self.indexer = DefaultIndexer(default_index_algorithm, self.fs, self.md_adapter)
            self.index = self.indexer.run()

    def get_document(self, document_id: str | IndexMetadataModel = None) -> T:
        if document_id is None:
            return self.md_adapter.extract(self.fs.open_document())
        else:
            return self.fs.open_document(document_id)

    def get_index_entry(self, *args) -> list[IndexMetadataModel] | None:

        collection_id, = args

        i: IndexMetadataModel
        index_entries: list = []

        if collection_id is None:
            try:
                return [self.index[0]]
            except:
                raise ValueError("No collection found in index")
        else:
            for i in self.index:
                if i.id == collection_id:
                    index_entries.append(i)
        return index_entries

    def get_index_count(self, *args) -> int:
        collection_id, = args

        i: IndexMetadataModel
        index_entries: list = []
        for i in self.index:
            if i.id == collection_id and i.depth:
                index_entries.append(i)

        return len(index_entries)

    def get_index_children_count(self, *args) -> int:
        collection_id, = args

        i: IndexMetadataModel

        counter = 0
        for i in self.index:
            if i.id == collection_id:
                counter += i.children_count

        return counter

    def attach_adapter(self, adapter):
        self.md_adapter = adapter

    def attach_fs(self, fs):
        self.fs = fs