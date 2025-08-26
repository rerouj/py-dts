from typing import Protocol


class Service(Protocol):
    def get(self):
        ...
    def update(self):
        ...
    def delete(self):
        ...
    def create(self):
        ...

class CollectionService:
    def get(self):
        pass
    def update(self):
        pass
    def delete(self):
        pass
    def create(self):
        pass
