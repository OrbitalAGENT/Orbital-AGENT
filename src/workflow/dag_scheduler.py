# src/workflow/dag_scheduler.py
import networkx as nx
from typing import List, Dict
from datetime import datetime

class TaskNode:
    def __init__(self, task_id: str, dependencies: List[str]):
        self.task_id = task_id
        self.dependencies = dependencies
        
class DAGScheduler:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.execution_order = []
        
    def add_task(self, task: TaskNode) -> None:
        self.graph.add_node(task.task_id)
        for dep in task.dependencies:
            self.graph.add_edge(dep, task.task_id)
            
    def validate_dag(self) -> bool:
        try:
            self.execution_order = list(nx.topological_sort(self.graph))
            return True
        except nx.NetworkXUnfeasible:
            return False
            
    def next_tasks(self) -> List[str]:
        return [node for node in self.graph.nodes() 
                if not list(self.graph.predecessors(node))]
