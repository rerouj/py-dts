from typing import Protocol

from dts_api.classes.Adapter import Adapter
from dts_api.classes.FileStorage import FileStorage


class Indexer(Protocol):

    def __init__(self, index_algorithm):
        self.index_algorithm=index_algorithm

    def run(self):
        ...

class DefaultIndexer:
    def __init__(self, index_algorithm, fs: FileStorage, adapter: Adapter):
        self.fs: FileStorage=fs
        self.__index_algorithm=index_algorithm
        self.adapter=adapter

    def run(self):
        return self.__index_algorithm(self.adapter.extract(self.fs.open_document())) # default behaviour opens metadata file