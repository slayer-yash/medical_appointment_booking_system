from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
# from pydantic.generics import GenericModel

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool
    status_code: int
    message: Optional[str] = None
    total_records: Optional[int] = 1
    current_page: Optional[int] = 1
    data: Optional[T] = None