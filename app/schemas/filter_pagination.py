from pydantic import BaseModel, create_model, field_validator
from typing import Any
from typing import List, Optional
import operator

class FilterOperator(str):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    LIKE = "like"

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

OPERATOR_MAP = {
    FilterOperator.EQ: operator.eq,
    FilterOperator.NE: operator.ne,
    FilterOperator.GT: operator.gt,
    FilterOperator.LT: operator.lt,
    FilterOperator.GTE: operator.ge,
    FilterOperator.LTE: operator.le,
}