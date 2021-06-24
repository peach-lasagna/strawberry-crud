from typing import Any, Callable, Optional, Type, NewType

import strawberry
from strawberry.type import _process_type
from dataclasses import make_dataclass, fields
from strawberry.custom_scalar import ScalarWrapper
import copy


class MissingValue:
    pass

class Config:
    delete_all = True
    get_all    = True
    # autogenerate_schema = False 

class BaseCrud:
    def __init__(
        self,
        get_db: Callable,
        cls: Type, # dataclass
        db_model: Any = None, # Table
        update_schema: Type = None, # strawberry.input
        config: Config = None,
        name: str = None, # name for routes
        void_scalar: ScalarWrapper = None, # for null responses
    ):
        # assert schema is not None and db_model is not None, "schema or db_model must not equal None"

        self.config = Config() if config is None else config
        self.name = cls.__name__.title() if name is None else name
        # if schema is None:
        #     raise UnboundLocalError() # TODO schema generation from model
        #     # self.schema = self._convert_model(db_model)
        #     # self.model = db_model
        #     # self._input_create = _process_type(self.schema, is_input=True)
        # else:
        #     self.model = db_model
        self.cls = cls
        self.model = cls if db_model is None else db_model
        
        _cls = make_dataclass(cls.__name__, [(f.name, f.type, f.default) for f in fields(cls)]) # type: ignore
        self._input_create = _process_type(_cls, is_input=True, name=f"InputCreate{self.name}")
        if update_schema is None:
            _cls = make_dataclass(cls.__name__, [(f.name, Optional[f.type], MissingValue) for f in fields(cls)]) # type: ignore
            self._input_update = _process_type(_cls, is_input=True, name=f"InputUpdate{self.name}")
        else:
            self._input_update = update_schema

        self.schema = strawberry.type(copy.copy(cls))
        # self.schema = cls
        self.get_db = get_db

        if void_scalar is None:
            func = lambda _: None
            self.void = strawberry.scalar(
                NewType("Void", object),
                serialize=func,
                parse_value=func
            )
        else:
            self.void = void_scalar

        self.__post_init__()


    def query(self) -> Type:
        fields = {
            f"get{self.name}": strawberry.field(self._get_one()),
        }
        if self.config.get_all:
            val = {f"get{self.name}s": strawberry.field(self._get_all())}
            fields.update(val)
        Query = type(f"Query{self.name}", (object,), fields)
        return strawberry.type(Query)

    def mutation(self) -> Type:
        fields = {
            f"create{self.name}": strawberry.mutation(self._create()),
            f"delete{self.name}": strawberry.mutation(self._delete_one()),
            f"update{self.name}": strawberry.mutation(self._update()),
        }
        if self.config.delete_all:
            val = {f"delete{self.name}s": strawberry.mutation(self._delete_all())}
            fields.update(val)
        Mutation = type(f"Mutation{self.name}", (object,), fields)
        return strawberry.type(Mutation)
    
    def _get_all(self):
        raise NotImplementedError()

    def _get_one(self):
        raise NotImplementedError()

    def _create(self):
        raise NotImplementedError()
    
    def _update(self):
        raise NotImplementedError()

    def _delete_one(self):
        raise NotImplementedError()
    
    def _delete_all(self):
        raise NotImplementedError()

    #async def _convert_model(self, db_model):
    #     raise NotImplementedError()

    def __post_init__(self):
        pass
