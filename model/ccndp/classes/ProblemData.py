from __future__ import annotations

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np

from ccndp.utils import JsonStorableMixin


from .Edge import Edge
from .FacilityNode import FacilityNode
from .Node import Node
from .Resource import Resource
from .Result import Result
from .SinkNode import SinkNode
from .SourceNode import SourceNode
from .StorageNode import StorageNode


@dataclass(frozen=False)
class ProblemData(JsonStorableMixin):
    """
    Problem data instance.

    Parameters
    ----------
    nodes
        Array of nodes.
    edges
        Array of edges.
    resources
        Array of resources. These are consumed and created by facilities.
    num_scenarios
        Number of scenarios.
    """

    nodes: list[Node]
    edges: list[Edge]
    resources: list[Resource]
    num_scenarios: int

    def __hash__(self) -> int:
        """
        Returns a hash based on the size properties of the data instance:
        number of nodes, number of edges, and the number of scenarios.
        """
        return hash(
            (
                len(self.nodes),
                len(self.edges),
                len(self.resources),
                self.num_scenarios,
            )
        )

    @property
    def num_nodes(self) -> int:
        return len(self.nodes)

    @property
    def num_edges(self) -> int:
        return len(self.edges)

    @property
    def num_resources(self) -> int:
        return len(self.resources)

    def costs(self) -> np.ndarray:
        return np.array([edge.cost for edge in self.edges])

    def vtypes(self) -> np.ndarray:
        return np.array([edge.vtype for edge in self.edges])

    def edge_indices_from(self, node: Node) -> list[int]:
        """
        Implements O(i) from the paper, for a given vertex i.
        """
        return [
            idx
            for idx, edge in enumerate(self.edges)
            if edge.frm == node and edge.to != node
        ]

    def edge_indices_to(self, node: Node, res: Resource = None) -> list[int]:
        """
        Implements I(i, r) and I(i) from the paper, for a given vertex i and
        optional resource r.
        """
        edges = [
            idx
            for idx, edge in enumerate(self.edges)
            if edge.to == node and edge.frm != node
        ]

        if not res:  # return I(i)
            return edges

        return [  # return I(i, r)
            idx
            for idx in edges
            if self.edges[idx].frm.makes == res  # type: ignore
        ]

    def edge_index_of(self, pair: tuple[Node, Node]) -> int:
        for idx, edge in enumerate(self.edges):
            if pair == (edge.frm, edge.to):
                return idx

        raise LookupError(f"Could not find edge {pair} in the edge set.")

    def sources(self) -> list[SourceNode]:
        return [node for node in self.nodes if isinstance(node, SourceNode)]

    def facilities(self) -> list[FacilityNode]:
        return [node for node in self.nodes if isinstance(node, FacilityNode)]

    def sinks(self) -> list[SinkNode]:
        return [node for node in self.nodes if isinstance(node, SinkNode)]

    def storages(self) -> list[StorageNode]:
        return [node for node in self.nodes if isinstance(node, StorageNode)]

    def plot_solution(self, res: Result, ax: plt.Axes | None = None):
        if ax is None:
            _, ax = plt.subplots(figsize=(12, 12))


        # Several plot settings, partially grouped by node type.
        marker_size = 144
        plot_kwargs = dict(
            src=dict(c="black", marker="^", label="Source facilities"),
            fac=dict(c="red", marker="o", label="Facilities"),
            sink=dict(c="green", marker="s", label="Consumers"),
            storage=dict(c="blue", marker="S", label="Storage")
        )

        # Locations of various node types. Nodes are only plotted when they're
        # in the construction decisions. Of course, sinks are always plotted.
        group_data: dict[str, list | np.ndarray] = dict(src=[], fac=[])
        group_data["sink"] = np.array([sink.loc for sink in self.sinks()])
        group_data["storage"] = np.array([storage.loc for storage in self.storages()])

        # Go through all decisions and store/annotate all those that have been
        # constructed (i.e., have a value > 0).
        for (k, v), edge in zip(res.decisions.items(), self.edges):
            if np.isclose(v, 0.0):  # not constructed
                continue

            if edge.frm != edge.to:  # plot regular edges
                locs = np.array([edge.frm.loc, edge.to.loc])
                x, y = locs[:, 0], locs[:, 1]
                ax.plot(x, y, linewidth=1, color="tab:blue")
                annotate(ax, [v], [np.array([np.mean(x), np.mean(y)])])
            else:  # annotate nodal decisions
                if isinstance(edge.frm, SourceNode):
                    group = "src"
                elif isinstance(edge.to, FacilityNode):
                    group = "fac"
                group_data[group].append(edge.frm.loc)
                annotate(ax, [v], [np.array(edge.frm.loc)])

        for group in ["src", "fac", "sink", "storage"]:  # plot nodal decisions
            data = np.array(group_data[group])
            kwargs = dict(zorder=2.5, **plot_kwargs[group])
            ax.scatter(data[:, 0], data[:, 1], marker_size, **kwargs)

        demand = np.array([sink.demand.mean() for sink in self.sinks()])
        annotate(ax, demand, group_data["sink"])  # annotate average demand

        ax.xaxis.set_major_locator(plt.NullLocator())
        ax.yaxis.set_major_locator(plt.NullLocator())

        ax.set_title("Construction decisions", fontsize=20)
        ax.legend(frameon=False, fontsize=14, ncol=3, loc="lower center")

        plt.tight_layout()
        plt.draw_if_interactive()



def annotate(ax: plt.Axes, items: np.array, locations: np.array):
    style = dict(bbox=dict(boxstyle="round", fc="w"), fontsize=8)

    for i, (loc, num) in enumerate(zip(locations, items)):
        ax.annotate(f"{num:.1f}", loc + 0.05, **style)
