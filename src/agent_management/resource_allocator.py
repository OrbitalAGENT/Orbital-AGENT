# orbital-agent/src/agent_management/resource_allocator.py
import logging
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"

@dataclass
class NodeResources:
    total: Dict[ResourceType, float]
    allocated: Dict[ResourceType, float]
    last_updated: float

class ResourceAllocator:
    def __init__(self, allocation_strategy: str = "bin_packing"):
        self.nodes: Dict[str, NodeResources] = {}
        self.lock = threading.RLock()
        self.strategy = allocation_strategy
        self._initialize_strategies()

    def _initialize_strategies(self):
        self._strategy_map = {
            "bin_packing": self._bin_packing_strategy,
            "spread": self._spread_strategy,
            "random": self._random_strategy
        }

    def register_node(self, node_id: str, resources: Dict[ResourceType, float]):
        with self.lock:
            self.nodes[node_id] = NodeResources(
                total=resources.copy(),
                allocated={rt: 0.0 for rt in resources},
                last_updated=time.time()
            )
        logger.info(f"Registered node {node_id} with resources: {resources}")

    def allocate_resources(self, requirements: Dict[ResourceType, float]) -> List[Tuple[str, Dict[ResourceType, float]]]:
        with self.lock:
            strategy_fn = self._strategy_map.get(self.strategy)
            if not strategy_fn:
                raise ValueError(f"Unknown allocation strategy: {self.strategy}")

            return strategy_fn(requirements)

    def _bin_packing_strategy(self, requirements: Dict[ResourceType, float]) -> List[Tuple[str, Dict[ResourceType, float]]]:
        allocations = []
        remaining = requirements.copy()
        
        sorted_nodes = sorted(
            self.nodes.items(),
            key=lambda item: self._calculate_node_fitness(item[1], remaining),
            reverse=True
        )

        for node_id, node_res in sorted_nodes:
            alloc = self._allocate_from_node(node_id, remaining)
            if alloc:
                allocations.append((node_id, alloc))
                for rt in remaining:
                    remaining[rt] -= alloc.get(rt, 0.0)
                    if remaining[rt] <= 0.001:
                        del remaining[rt]
                if not remaining:
                    break

        if remaining:
            raise RuntimeError(f"Failed to allocate resources: {remaining} remaining")

        return allocations

    def _calculate_node_fitness(self, node: NodeResources, requirements: Dict[ResourceType, float]) -> float:
        available = {
            rt: node.total[rt] - node.allocated[rt]
            for rt in requirements
            if rt in node.total
        }
        
        if not all(available.get(rt, 0) >= req for rt, req in requirements.items()):
            return -1

        return sum(available.values()) / sum(node.total.values())

    def _allocate_from_node(self, node_id: str, requirements: Dict[ResourceType, float]) -> Optional[Dict[ResourceType, float]]:
        node_res = self.nodes[node_id]
        allocation = {}
        
        for rt, req in requirements.items():
            available = node_res.total[rt] - node_res.allocated[rt]
            if available <= 0:
                return None
            alloc_amount = min(req, available)
            allocation[rt] = alloc_amount
            node_res.allocated[rt] += alloc_amount
        
        node_res.last_updated = time.time()
        return allocation

    def release_resources(self, node_id: str, resources: Dict[ResourceType, float]):
        with self.lock:
            if node_id not in self.nodes:
                logger.warning(f"Attempted to release resources from unknown node: {node_id}")
                return

            node_res = self.nodes[node_id]
            for rt, amount in resources.items():
                if rt not in node_res.allocated:
                    continue
                node_res.allocated[rt] = max(node_res.allocated[rt] - amount, 0.0)
            node_res.last_updated = time.time()

    def update_node_resources(self, node_id: str, new_total: Dict[ResourceType, float]):
        with self.lock:
            if node_id not in self.nodes:
                logger.error(f"Update failed: Node {node_id} not registered")
                return

            current = self.nodes[node_id]
            for rt in current.total:
                if rt not in new_total:
                    new_total[rt] = current.total[rt]

            self.nodes[node_id] = NodeResources(
                total=new_total.copy(),
                allocated=current.allocated.copy(),
                last_updated=time.time()
            )

    def get_node_utilization(self, node_id: str) -> Dict[ResourceType, float]:
        with self.lock:
            node_res = self.nodes.get(node_id)
            if not node_res:
                raise ValueError(f"Unknown node: {node_id}")
            
            return {
                rt: node_res.allocated[rt] / node_res.total[rt]
                for rt in node_res.total
            }

    def set_allocation_strategy(self, strategy: str):
        with self.lock:
            if strategy not in self._strategy_map:
                raise ValueError(f"Invalid strategy: {strategy}")
            self.strategy = strategy
            logger.info(f"Changed allocation strategy to: {strategy}")
