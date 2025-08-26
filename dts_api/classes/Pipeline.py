from functools import reduce
from typing import Protocol, Callable

from dts_api.funcs.common import get_citation_trees, select_tree, prepare_path, prepare_md_path, tag_original_document, \
    build_toc, complete_ref


class PipelineBuilder(Protocol):
    def get_pipeline(self, pipeline: str = 'toc'):
        ...
    def pipeline(self, func_array: list[Callable]):
        ...

class TocPipelineBuilder:

    def __init__(self):
        self.toc_func_array = [get_citation_trees, select_tree, prepare_path, prepare_md_path, tag_original_document, build_toc, complete_ref]
        self.toc_func_test = []
        self.toc_func_array.reverse()
        self.toc_func_test.reverse()

    def get_pipeline(self, pipeline: str = 'toc'):
        if pipeline == 'toc':
            return self.run(self.toc_func_array)
        if pipeline == 'test':
            return self.run(self.toc_func_test)

    @staticmethod
    def run(func_array: list[Callable]):
        return reduce(lambda g, h: lambda *args: g(h(*args)), func_array)