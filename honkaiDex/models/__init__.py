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
            
        if name in cls._instances[cls]:
            raise ValueError(f"{name} already exists")
        
        instance = super().__call__(*args, **kwargs)
        cls._instances[cls][name] = instance
        
        return instance

class HondexModel(BaseModel, metaclass=HondexMeta):
    name : str
    summary : str