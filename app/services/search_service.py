from app.config.search_parameters import search_parameters
from app.utils.logging import Logging
from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from sqlalchemy import String
from sqlalchemy.orm.attributes import InstrumentedAttribute

def is_string_column(column):
    return isinstance(column.property.columns[0].type, String)

logger = Logging(__name__).get_logger()

# from app.exceptions.search_exceptions import *

class SearchService():
    def __init__(self, db, model):
        self.db = db
        self.model = model

    def search_record(self, search_param):
        logger.info(f"Starting search for: {search_param}")
        model_config = search_parameters.get(self.model)
        if not model_config:
            logger.warning(f"No search configuration found for model: {self.model}")

        records = self.db.query(self.model)
        filters = []
        search_param = f"%{search_param.strip()}%"

        for column in model_config['self']:
            try:
                filter_field = getattr(self.model, column)
                if isinstance(filter_field, InstrumentedAttribute) and is_string_column(filter_field):
                    filters.append(filter_field.ilike(search_param))
                    logger.debug(f"Search filter added for self field: {column}")
            except AttributeError:
                logger.warning(f"Invalid self field: {column}")
                raise HTTPException(500, "search column field is invalid: {column}")

        for rel_attr_name, rel_fields in model_config['relationships'].items():
            try:
                rel_attr = getattr(self.model, rel_attr_name)
                related_model = rel_attr.property.mapper.class_
                alias = aliased(related_model)
                records = records.outerjoin(alias, rel_attr)

                for column in rel_fields:
                    try:
                        filter_field = getattr(alias, column)
                        if isinstance(filter_field, InstrumentedAttribute) and is_string_column(filter_field):
                            filters.append(filter_field.ilike(search_param))
                            logger.debug(f"Search filter added for related field: {rel_attr_name}.{column}")
                    except AttributeError:
                        logger.warning(f"Invalid related field: {rel_attr_name}.{column}")
                        HTTPException(500, f"Search parameter relation field is invalild :{rel_attr_name}.{column} ")
            except AttributeError:
                logger.warning(f"Invalid relationship attribute: {rel_attr_name}")
                HTTPException(500, f"Invalid relationship attribute: {rel_attr_name}")

        # records = records.filter(or_(*filters)).distinct()
        search_filters = filters
        # logger.info("Search completed successfully")
        return records, search_filters
