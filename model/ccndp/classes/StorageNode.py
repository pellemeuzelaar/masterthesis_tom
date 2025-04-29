from dataclasses import dataclass

import numpy as np

from .Node import Node
from .Resource import Resource


@dataclass(frozen=True)
class StorageNode(Node):
    """
    Represents a storage node in the model graph.
    """

    needs: Resource  # the resource demanded at this sink
    storage: np.array  # storage capacity at this sink, indexed by scenario

    def __str__(self) -> str:
        return f"storage[{self.idx}]"
