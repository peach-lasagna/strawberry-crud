from typing import Any, Callable, List, Optional, Type, Union
from sqlalchemy import select, delete, update
# from sqlalchemy.sql.schema import Table
from strawberry.types import Info
from ..base import BaseCrud, MissingValue
from ..utils import type_of_field, get_selections
# from .converter import sqlalchemy_to_dataclass
# from strawberry.type import _check_field_annotations
from dataclasses import asdict


try:
    from sqlalchemy.exc import IntegrityError
except ImportError:
    Model = Session = Any


class SqlalchemyCRUD(BaseCrud):
    def __post_init__(self):
        self.pk: str = self.cls.__table__.primary_key.columns.keys()[0]
        self.pk_type: type = type_of_field(self.cls, self.pk) # type: ignore

    def _get_fields(self, info: Info):
        return (getattr(self.cls, field.name.value) for field in get_selections(info)) # type: ignore

    def _get_all(_self):
        async def _get_all(self, info: Info) -> List[_self.schema]:
            statement = select(_self._get_fields(info))
            ses = await _self.get_db()
            res = await ses.execute(statement)
            return res.all()
        return _get_all

    def _get_one(_self):
        async def _get_one(self, item_id: _self.pk_type, info: Info) -> _self.schema:
            statement = select(_self._get_fields(info)).where(getattr(_self.cls, _self.pk) == item_id)
            ses = await _self.get_db()
            res = await ses.execute(statement)
            item = res.first()
            if item is not None:
                return item
            raise Exception(f"{_self.name} not found.")
        return _get_one

    def _update(_self):
        async def _update(self, item_id: _self.pk_type, update_schema: _self._input_update) -> Optional[_self.void]:
            update_data = asdict(update_schema, dict_factory=lambda lst:{el[0]:el[1] for el in lst if el[1] != MissingValue})
            statement = update(_self.model).where(getattr(_self.cls, _self.pk) == item_id).values(**update_data)
            ses = await _self.get_db()
            await ses.execute(statement)
            await ses.commit()
            return _self.void
        return _update

    def _create(_self):
        async def _create(self, schema: _self._input_create) -> Optional[_self.void]:
            db = await _self.get_db()
            try:
                db.add(schema)
                await db.commit()
                await db.refresh(schema) 
            except IntegrityError:
                await db.rollback()
                # raise HTTPException(422, "Key already exists")
            return _self.void
        return _create

    def _delete_one(_self):
        async def _delete_one(self, item_id: _self.pk_type) -> Optional[_self.void]: 
            statement = delete(_self.model).where(getattr(_self.cls, _self.pk) == item_id)
            db = await _self.get_db()
            await db.execute(statement)
            await db.commit()
            # await db.refresh(_self.model)
            return _self.void
        return _delete_one

    def _delete_all(_self):
        async def _delete_all(self) -> Optional[_self.void]:
            statement = delete(_self.model)
            db = await _self.get_db()
            await db.execute(statement)
            await db.commit()
            # await db.refresh(_self.model)
            return _self.void
        return _delete_all

    # def _convert_model(self, db_model: Table):
    #     def check(cls):
    #         _check_field_annotations(cls)
    #         return cls
    #     return sqlalchemy_to_dataclass(db_model, pre_init=check)
