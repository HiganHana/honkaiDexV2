from pydantic import BaseModel
from pydantic.main import ModelMetaclass

class HondexMeta(ModelMetaclass):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        name = kwargs.get("name", None)
        if name is None:
            raise ValueError("name is required")
        
        if cls not in cls._instances:
            cls._instances[cls] = {}
            
        if name not in cls._instances[cls]:
            cls._instances[cls][name] = super().__call__(*args, **kwargs)
        
        return cls._instances[cls][name]

class HondexModel(BaseModel, metaclass=HondexMeta):
    name : str
    summary : str