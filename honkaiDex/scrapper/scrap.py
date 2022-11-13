from mediawiki import MediaWiki
from pydantic import BaseModel, validator
from logging import getLogger

from honkaiDex.models import HondexModel

logger = getLogger(__name__)

url = "honkaiimpact3.fandom.com"

https_url = f"https://{url}/"

api_url = f"https://{url}/api.php"

wiki_instance = MediaWiki(url=api_url,  rate_limit=True)

class Scrapjob(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    category : str
    saveStr : str
    parseTo : type
    
    @validator("parseTo")
    def parseTo_validator(cls, v):
        if not issubclass(v, HondexModel):
            raise ValueError("parseTo must be a subclass of HondexModel")
        
        return v
    
    def scrap(self):
        raw = wiki_instance.categorytree(self.category, depth=1)
        if raw.get("links", None) is None:
            logger.error(f"Category {self.category} not found")
            return
        
        for link in raw["links"]:
            pass