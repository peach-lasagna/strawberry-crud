# from typing import Callable, TypeVar
# from sqlalchemy import Table
# from sqlalchemy.inspection import inspect
# from dataclasses import dataclass

# T = TypeVar

# def sqlalchemy_to_dataclass(db_model: Table, pre_init: Callable[[T], T]):
#     class cls:
#         pass
#     for column in inspect(db_model).columns:
#         pass

#     cls = pre_init(cls) # type: ignore
#     return dataclass(cls)
