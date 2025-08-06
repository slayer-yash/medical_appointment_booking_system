
from pydantic import BaseModel
from datetime import datetime
from fastapi import Query
from typing import Optional

class DateFilterSchema(BaseModel):
    start_date: Optional[datetime] = Query(None, description="filter start date")
    end_date: Optional[datetime] = Query(None, description="filter end date")