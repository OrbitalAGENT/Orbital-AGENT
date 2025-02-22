# orbital-agent/src/agent_management/swarm_engine.py
import json
import logging
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class NodeState:
    capacity: int
    load: int = 0
    last_heartbeat: float = 0.0

class SwarmOrchestrator:
    def __init__(self, config_file: str):
        self.nodes: Dict[str, NodeState] = {}
        self.executor = ThreadPoolExecutor()
        self.load_topology(config_file)
        
    def load_topology(self, config_path: str):
        """Load node network topology from config"""
        try:
            with open(config_path) as f:
                topology = json.load(f)
                self.nodes = {n['id']: NodeState(n['capacity']) for n in topology['nodes']}
            logger.info(f"Loaded swarm topology with {len(self.nodes)} nodes")
        except Exception as e:
            logger.error(f"Topology loading failed: {str(e)}")
            raise

    def allocate_task(self, task_resources: Dict) -> List[str]:
        """Distribute task using modified bin packing algorithm"""
        sorted_nodes = sorted(self.nodes.items(), 
                            key=lambda x: x[1].capacity - x[1].load,
                            reverse=True)
        
        allocated = []
        remaining = task_resources['requirements']
        
        for node_id, state in sorted_nodes:
            if state.load + remaining <= state.capacity:
                state.load += remaining
                allocated.append(node_id)
                remaining = 0
                break
            elif state.capacity - state.load > 0:
                allocated.append(node_id)
                remaining -= (state.capacity - state.load)
                state.load = state.capacity
                
        if remaining > 0:
            raise RuntimeError("Insufficient swarm resources")
            
        return allocated

    def release_resources(self, node_ids: List[str]):
        """Release allocated resources from nodes"""
        with self.executor.lock:
            for nid in node_ids:
                if nid in self.nodes:
                    self.nodes[nid].load = 0
