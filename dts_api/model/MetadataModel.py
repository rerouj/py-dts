from typing import Optional

from pydantic import BaseModel, Field


class IndexMetadataModel(BaseModel):

    id: str
    path: str
    location: Optional[str] = Field(default=None)
    depth: int = Field(default=None)
    key: str = Field(default=None)
    parent: str = Field(default=None)
    children_count: int = 0
    citation_trees: Optional[list] = Field(default=None)
    type: str = Field(default="collection")

    def model_post_init(self, __context):
        self.set_key()
        self.set_path()
        self.set_depth()
        self.set_parent()

    def set_depth(self):
        self.depth = int(self.path.count('.')/2)
    def set_key(self):
        # I don't know why this is important...
        self.key = self.path.split('.')[-1]
    def set_path(self):
        self.path = self.path.rsplit('.', 1)[0]
    def set_parent(self):
        if self.depth == 0:
            self.parent = 'root'
        else:
            self.parent = self.path.rsplit('.', 2)[0]