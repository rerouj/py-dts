# from dts_api.classes.tmp import Observer
from dts_api.classes.Adapter import AbstractIngestor, AbstractExtractor

class CustomIngestor(AbstractIngestor):
    def __call__(self, *args, **kwargs):
        pass

class CustomExtractor(AbstractExtractor):
    def __call__(self, *args, **kwargs):
        print("Custom Extractor: extract content")

class CustomMetadataAdapter:
    def __init__(self, ingestor, extractor):
        self.ingestor: AbstractIngestor = ingestor
        self.extractor: AbstractExtractor = extractor
    def ingest(self, *args, **kwargs):
        pass
    def extract(self):
        self.extractor()