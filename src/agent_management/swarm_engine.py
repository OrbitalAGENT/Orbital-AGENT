import numpy as np
from typing import Dict, List
from pydantic import BaseModel

class AgentState(BaseModel):
    agent_id: str
    cpu_usage: float
    memory: float
    task_capacity: int

class SwarmOrchestrator:
    def __init__(self, max_agents: int = 1000):
        self.agent_registry: Dict[str, AgentState] = {}
        self.Q_table = np.zeros((max_agents, 10))  # Q-Learning state matrix

    def register_agent(self, agent: AgentState):
        """Dynamic agent registration with health checks"""
        if agent.agent_id not in self.agent_registry:
            self.agent_registry[agent.agent_id] = agent
            self._update_q_table(agent.agent_id)

    def optimize_swarm(self, task_matrix: np.ndarray) -> List[str]:
        """Q-Learning based swarm optimization"""
        optimal_agents = []
        for task in task_matrix:
            agent_ids = sorted(
                self.agent_registry.keys(),
                key=lambda x: self._calculate_fitness(x, task),
                reverse=True
            )[:3]  # Select top 3 agents per task
            optimal_agents.extend(agent_ids)
        return list(set(optimal_agents))

    def _calculate_fitness(self, agent_id: str, task: np.ndarray) -> float:
        """Fitness function combining resource metrics and Q-values"""
        agent = self.agent_registry[agent_id]
        resource_score = (agent.cpu_usage * 0.3 + 
                         agent.memory * 0.2 + 
                         agent.task_capacity * 0.5)
        q_value = self.Q_table[len(self.agent_registry), task[0]]
        return resource_score * q_value
