from typing import Any, Annotated

from pydantic import AfterValidator
from pydantic_core.core_schema import ValidationInfo


def out_of_range_int(value: Any, info: ValidationInfo):
    minimal_value = 0
    if info.field_name == 'down':
        minimal_value = -1
    if value < minimal_value or value > 1000000:
        raise ValueError(f"{info.field_name} is out of range")
    # todo: raise internal error for int larger than 100000
    return value


out_of_range_int = Annotated[int, AfterValidator(out_of_range_int)]