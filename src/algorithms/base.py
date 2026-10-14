
from dataclasses import dataclass, field


@dataclass
class PathfindingResult:
    path: list
    distance: float
    nodes_explored: int
    algorithm: str
    explored_nodes: list = field(default_factory=list)

    @property
    def found(self):
        return bool(self.path)
