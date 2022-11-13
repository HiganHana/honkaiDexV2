from pydantic import BaseModel, Field, validator
import typing

_counter = 0

class a1(BaseModel):
    other1 : int
    other2 : str
    other3 : typing.Optional[str] = Field(default_factory=lambda : "default")
    
    @validator("other3", pre=True)
    def check_if_default(cls, v):
        global _counter
        if v == "default" or v is None:
            v = f"new_default_{_counter}"
            _counter += 1
        return v

class a2(BaseModel):
    something : typing.List[typing.Any]

class a3(BaseModel):
    test1 : typing.List[a2]
    test2 : typing.Dict[str, a1]
    test3 : int

import unittest

class test_poc_pydantic(unittest.TestCase):
    def test_x(self):
        x = a3(
            **{
                "test1" : [
                    {
                        "something" : [1,2,3]
                    },
                    {
                        "something" : [4,5,6]
                    }
                ],
                "test2" : {
                    "a" :  {
                        "other1" : 3,
                        "other2" : "2132",
                        "other3" : "default"
                    },
                    "b" :  {
                        "other1" : 31,
                        "other2" : "213x",
                        "other3" : "x"
                    }
                },
                "test3" : 3
            }
        )
    
        pass