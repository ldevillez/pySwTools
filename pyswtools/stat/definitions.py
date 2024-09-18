from enum import Enum
from dataclasses import dataclass, asdict


class TypeComponent(str, Enum):
    """Class represeting an type of parts"""

    PART = "part"
    ASSEMBLY = "assembly"
    ALL = "all"


class TypeOutput(str, Enum):
    """Class represeting an output type"""

    TREE = "tree"
    LIST = "list"


class TypeSort(str, Enum):
    """Class represeting an output type"""

    MASS = "mass"
    MASS_PART = "mass-part"
    NAME = "name"


@dataclass
class StatComponentTree:
    number: int
    children: list

    def dict(self):
        return {k: v for k, v in asdict(self).items()}


@dataclass
class StatComponent:
    mass: float
    density: float
    number: int
    typeComponent: TypeComponent
    numberDrawing: int

    def dict(self):
        return {k: v for k, v in asdict(self).items()}
