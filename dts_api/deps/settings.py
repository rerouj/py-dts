from typing import Annotated

from fastapi import Depends

from dts_api.settings.settings import Settings, get_settings

settings = Annotated[Settings, Depends(get_settings)]