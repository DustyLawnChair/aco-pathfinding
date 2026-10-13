
from dataclasses import dataclass


@dataclass
class PathfindingResult:
    path: list
    distance: float
    nodes_explored: int
    algorithm: str

    @property
    def found(self):
        return bool(self.path)
