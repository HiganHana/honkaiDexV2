from pydantic import BaseModel
from honkaiDex.models import HondexModel
from honkaiDex.models.character import Character

class Battlesuit(HondexModel):
    character : Character
    version : str
    rank : str
    type : str
    core_strengths : str
    leader : str
    leaderEffect : str
    special : str
    specialEffect : str
    passive : str
    passiveEffect : str
    ultimate : str
    ultimateEffect : str
    evasion : str
    evasionEffect : str
    basic : str
    basicEffect : str
    core : str = None
    profile : str = None
    img : str = None