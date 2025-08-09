from app.schemas.filter_pagination import OPERATOR_MAP
from app.utils.logging import Logging
from fastapi import HTTPException
from sqlalchemy import or_
# from app.exceptions.filter_pagination_exceptions import *
# from app.exceptions.base import AppException

logger = Logging(__name__).get_logger()

class FilterPaginationService:
    def __init__(self, model, allowed_fields, db):
        self.model = model
        self.allowed_fields = allowed_fields
        self.db = db

    def apply_filter_pagination(self, filters, sort_by, sort_order, page, limit, records, search_filters=None):
        logger.info("Starting filter and pagination process")
        self.verify_filters(filters, sort_by, sort_order, page, limit)

        if not records:
            records = self.db.query(self.model)

        records = self.apply_filter(filters, records, search_filters)
        records = records.distinct()
        logger.info(f"Filters applied successfully")
        records = self.apply_sorting(sort_by, sort_order, records)
        logger.info(f"Sorting applied successfully")

        offset = (page - 1) * limit
        
        total_records = records.count()
        paginated_records = records.offset(offset).limit(limit).all()

        logger.debug(f"Filtered {total_records} total records, returning page {page} with limit {limit}")
        return paginated_records, total_records

    def apply_filter(self, filters, records, search_filters):
        if filters is None:
            if search_filters:
                records = records.filter(or_(*search_filters))
            return records

        try:
            filters = filters.split(",")
            for filter in filters:
                field, condition, value = filter.split("-")
                field, value = field.strip(), value.strip()
                filter_field = getattr(self.model, field, None)

                if filter_field is None:
                    logger.warning(f"Ignored invalid filter field: {field}")
                    continue

                if condition == 'like':
                    # filter_conditions.append(filter_field.ilike(f"%{value}%"))
                    records = records.filter(filter_field.ilike(f"%{value}%"))
                else:
                    op = OPERATOR_MAP.get(condition)
                    if not op:
                        logger.warning(f"Unsupported operator: {condition}")
                        continue
                    # filter_conditions.append(op(filter_field, value))
                    records = records.filter(op(filter_field, value))

            if search_filters:
                records = records.filter(or_(*search_filters))
            return records
        except Exception as e:
            logger.exception(f"Error applying filters: {e}")
            raise HTTPException(500, f"Error applying filters: ")

    def apply_sorting(self, sort_by, sort_order, records):
        if sort_by is None:
            return records

        try:
            sort_field = getattr(self.model, sort_by)
            if sort_order == 'desc':
                return records.order_by(sort_field.desc())
            else:
                return records.order_by(sort_field.asc())
        except Exception as e:
            logger.exception(f"Error applying sorting: {e}")
            raise HTTPException(500, "Error applying sorting")

    def verify_filters(self, filters, sort_by, sort_order, page, limit):
        if filters:
            filters = filters.split(",")
            for filter in filters:
                filter_parts = filter.split("-")
                if len(filter_parts) != 3:
                    raise HTTPException(400, f"filter parameters needs to be in format field-operator-value, input filter: {filter}")

                field, condition, value = filter_parts
                if field.strip() not in self.allowed_fields:
                    raise HTTPException(400, f"invalid field in filter parameter, field:{field}, allowed_fields: {self.allowed_fields}")

                if condition == 'like' and not isinstance(value, str):
                    raise HTTPException(400, f"like operator requires a string value, input value: {value}")

        if sort_by and sort_by not in self.allowed_fields:
            raise HTTPException(400, f"invalid field in sort_by parameter, input sort_by: {sort_by}, allowed_fields: {self.allowed_fields}")

        if sort_order not in ["asc", "desc"]:
            raise HTTPException(400, f"sort order must be either 'asc' or 'desc', input sort_order: {sort_order}")

        if page < 1:
            raise HTTPException(400, f"page must be a positive integer, input page: {page}")

        if limit < 1 or limit > 100:
            raise HTTPException(400, f"limit must be an integer between 1 and 100, input limit: {limit}")