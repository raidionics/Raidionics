from aenum import Enum, unique
from typing import Any


def get_type_from_string(enum_type: Enum, string: str) -> Any:
    if type(string) == str:
        for i in range(len(list(enum_type))):
            #if string == list(EnumType)[i].name:
            if string == str(list(enum_type)[i]):
                return list(enum_type)[i]
        return -1
    elif type(string) == enum_type:
        return string
    else: #Unmanaged input type
        return -1
