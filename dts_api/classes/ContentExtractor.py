from typing import Protocol
from collections import deque
from dts_api.classes.Error import BadRangeError
from dts_api.classes.RepresentationBuilder import NavigationContentBuilder, DocumentContentBuilder


class ContentExtractor(Protocol):
    def extract_content(self, *args, **kwargs):
        ...

class CommonExtractor:
    """
    A common base class for content
    todo: add a content parser for different metadata content structure (c.f. utils.py l.49)
    """
    def __init__(self, prefix: str = None, namespace: str = "http://www.tei-c.org/ns/1.0", nsmap=None):
        if nsmap is None:
            nsmap = {'tei': 'http://www.tei-c.org/ns/1.0'}
        self.prefix = prefix
        self.namespace = namespace
        self.nsmap = nsmap

class JsonContentExtractor(CommonExtractor):
    """
    A simple static content extractor for JSON data.
    """

    def extract_content(self, *args, **kwargs):
        dataset, path = args
        if kwargs:
            _, = kwargs
        if path:
            queue = deque(path.split('.'))
            while queue:
                item = queue.popleft()
                path = '.'.join(queue)
                if item.isdigit():
                    item = int(item)
                    return self.extract_content(dataset[item], path)
                else:
                    dataset = dataset[item]
            return dataset
        return dataset

class NavigationContentExtractor(CommonExtractor):

    def __init__(self, prefix, namespace, nsmap):
        super().__init__(prefix, namespace, nsmap)
        self.content_builder = NavigationContentBuilder()

    def extract_content(self, *args, **kwargs):

        navigation: list | None = []
        navigation_info: list = [None, None, None]

        if args:
            _, = args
        resource, ref, start, end, down, tree, page, limit, offset, dts_resource, cite_structure, document = kwargs.values()
        toc = dts_resource.find("%sTableOfContent/CitationTree[@tree='%s']" % (self.namespace, tree))

        if ref and start is None and end is None and down is None:
            navigation_info = self.content_builder.get_navigation_info(toc=toc, ref=ref, nsmap=self.nsmap)
            navigation = None

        if ref is None and start and end and down is None:
            navigation_info = self.content_builder.get_navigation_info(nsmap=self.nsmap, toc=toc, start=start, end=end)
            navigation = None

        if ref is None and start is None and end is None and down:
            navigation = self.content_builder.get_root(down, toc)

        if ref and start is None and end is None and (down or down==0):
            try:
                navigation_info = self.content_builder.get_navigation_info(toc, self.nsmap, ref=ref)
                navigation = self.content_builder.get_content(ref, down, toc, self.nsmap)
            except ValueError as error:
                raise error

        if ref is None and start and end and (down or down==0):
            try:
                navigation_info = self.content_builder.get_navigation_info(toc, self.nsmap, start=start, end=end)
                navigation = self.content_builder.get_milestone(start, end, down, toc, document, self.nsmap)
            except BadRangeError as error:
                raise error

        citation_trees, max_cite_depth = self.content_builder.get_citation_trees(cite_structure)
        return navigation, navigation_info, citation_trees, max_cite_depth

class DocumentContentExtractor(CommonExtractor):

    def __init__(self, request, paginator, store):
        super().__init__(request, paginator, store)
        self.content_builder = DocumentContentBuilder()

    def extract_content(self, *args, **kwargs):
        if args:
            _, = args
        resource, ref, start, end, tree, media_type, dts_resource, cite_structure, document = kwargs.values()
        toc = dts_resource.find(".//%sTableOfContent/CitationTree[@tree='%s']" % (self.namespace, tree))

        content = []

        if ref is None and start is None and end is None:
            content = self.content_builder.get_root(dts_resource)

        if ref and start is None and end is None:
            try:
                content = self.content_builder.get_content(toc, ref, tree, document)
            except ValueError as error:
                raise error

        if ref is None and start and end:
            try:
                content = self.content_builder.get_milestone(toc, start, end, document, self.nsmap)
            except BadRangeError as error:
                raise error

        return content, dts_resource