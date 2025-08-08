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
            raise HTTPException()

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
            self.logger.exception(f"Error applying sorting: {e}")
            raise HTTPException()

    def verify_filters(self, filters, sort_by, sort_order, page, limit):
        if filters:
            filters = filters.split(",")
            for filter in filters:
                filter_parts = filter.split("-")
                if len(filter_parts) != 3:
                    raise HTTPException(filter)

                field, condition, value = filter_parts
                if field.strip() not in self.allowed_fields:
                    raise HTTPException(field, self.allowed_fields)

                if condition == 'like' and not isinstance(value, str):
                    raise HTTPException()

        if sort_by and sort_by not in self.allowed_fields:
            raise HTTPException(sort_by, self.allowed_fields)

        if sort_order not in ["asc", "desc"]:
            raise HTTPException()

        if page < 1:
            raise HTTPException()

        if limit < 1 or limit > 100:
            raise HTTPException()