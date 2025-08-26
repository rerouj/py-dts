from abc import ABC
from typing import TypeVar
from urllib.error import URLError

from fastapi import HTTPException

from dts_api.classes.Error import CollectionNotFoundError, ResourceNotFoundError
from dts_api.classes.Factory import RepresentationFactory
from dts_api.classes.Operator import Operator
from dts_api.classes.StoreKeeper import StoreKeeper
from dts_api.model.ParameterModel import CollectionParams, NavigationParams, DocumentParams

T = TypeVar("T")

class Service(ABC):
    def get(self, params: CollectionParams | NavigationParams | DocumentParams) -> T:
        ...
    def post(self, params: CollectionParams) -> T:
        ...
    def patch(self, params: CollectionParams) -> T:
        ...
    def delete(self, params: CollectionParams) -> T:
        ...


class CommonService:
    def __init__(self, representation_factory, storekeeper: StoreKeeper):
        self.representation_factory: RepresentationFactory = representation_factory
        self.storekeeper: StoreKeeper = storekeeper
        self.operator = Operator()

class CollectionService(CommonService):

    def get(self, params: CollectionParams):
        try:
            index, content = self.storekeeper.get_content(params)
            return self.representation_factory.build(params, index, content)
        except CollectionNotFoundError as e:
            raise HTTPException(404, f"{e.msg}")

    def post(self, params: CollectionParams):
        try:
            pass
        except FileNotFoundError:
            print(self.__str__(), params)
            raise HTTPException(404, detail="File not found")

class NavigationService(CommonService):

    def get(self, params) -> T:
        try:
            return self.representation_factory.build(*self.storekeeper.get_content(params), params)
        except ResourceNotFoundError as e:
            raise HTTPException(404, f"{e.msg}")
        except FileNotFoundError as e:
            msg, = e.args
            raise HTTPException(404, f"{msg}")

class DocumentService(CommonService):

    def get(self, params):
        try:
            return self.representation_factory.build(*self.storekeeper.get_content(params), params)
        except ResourceNotFoundError as e:
            raise HTTPException(404, f"{e.msg}")
        except URLError as e:
            raise e