from typing import Type


def type_of_field(schema: Type, name: str) -> Type:
    return schema.__annotations__[name]

def get_selections(info):
    return info.field_nodes[0].selection_set.selections

# def annotation_wrap(**kwa):
#     name = 
#     func = kwa.pop(tuple(kwa.keys())[-1])
#     ret_type = kwa.pop('return')
#     if ret_type is not None:
#         kwa['return'] = ret_type
#     func.__annotations__.update(kwa)
#     return func
