from fastapi import APIRouter

from . import collection, navigation, document, root

base_router = APIRouter()

base_router.include_router(root.router, prefix="", tags=["root"])
base_router.include_router(collection.router, prefix="/collection", tags=["collection"])
base_router.include_router(navigation.router, prefix="/navigation", tags=["navigation"])
base_router.include_router(document.router, prefix="/document", tags=["document"])


