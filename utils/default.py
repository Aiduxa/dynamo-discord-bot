__all__ = ['Default']

from dataclasses import dataclass

from discord import Object as D_Object


@dataclass
class Default:
    SERVER: D_Object = D_Object(id=1060218266670346370)
    PRIMARY_COLOR: int = int("1aff79", 16)
