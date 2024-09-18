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


class TypeExport(str, Enum):
    """Class represeting an export type"""

    NONE = "none"
    CSV = "csv"
    CLIPBOARD = "clipboard"


@dataclass
class StatComponentTree:
    """
    Class represting a component for a tree structure
    """

    number: int
    children: list

    def dict(self):
        """
        Convert the class to a dict structure
        """
        return {k: v for k, v in asdict(self).items()}


@dataclass
class StatComponent:
    """
    Class representing a component for the stat module
    """

    mass: float
    density: float
    number: int
    typeComponent: TypeComponent
    numberDrawing: int

    def dict(self):
        """
        Convert the class to a dict structure
        """
        return {k: v for k, v in asdict(self).items()}
