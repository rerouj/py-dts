import json
from abc import ABC, abstractmethod
from typing import Protocol

from dts_api.model.MetadataModel import IndexMetadataModel


class AbstractIngestor(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

class AbstractExtractor(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

class DefaultIngestor(AbstractIngestor):
    def __call__(self, *args, **kwargs):
        pass

class DefaultExtractor(AbstractExtractor):
    def __call__(self, *args, **kwargs) -> dict:
        print("Default Extractor: extract content")
        return json.loads(args[0])

class Adapter(Protocol):
    """
    a protocol that defines the interface for adapters.
    adapters are used to adapt different metadata file format to make them available to the store.
    use ingestors to control the loading/parsing of the metadata file.
    use extractors to control the extraction of the metadata content.
    """

    def __init__(self, ingestor, extractor):
        self.ingestor = ingestor
        self.extractor = extractor

    def ingest(self, *args, **kwargs):
        ...
    def extract(self, *args, **kwargs):
        ...

class JsonAdapter:

    def __init__(self, ingestor, extractor):
        self.ingestor: AbstractIngestor = ingestor
        self.extractor: AbstractExtractor = extractor
    def ingest(self, *args, **kwargs):
        pass
    def extract(self, *args, **kwargs):
        return self.extractor(*args, **kwargs)

class CsvAdapter:
    def __init__(self, ingestor, extractor):
        self.ingestor: AbstractIngestor = ingestor
        self.extractor: AbstractExtractor = extractor
    def ingest(self, *args, **kwargs):
        pass
    def extract(self, *args, **kwargs):
        pass
