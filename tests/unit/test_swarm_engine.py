import pytest
from src.agent_management.swarm_engine import SwarmOrchestrator, AgentState

def test_swarm_optimization():
    orchestrator = SwarmOrchestrator()
    
    # Register 10 agents with varying capacities
    for i in range(10):
        orchestrator.register_agent(
            AgentState(
                agent_id=f"agent_{i}",
                cpu_usage=0.2 + i*0.1,
                memory=1024 * (i+1),
                task_capacity=5 - i%3
            )
        )
    
    # Simulate task matrix
    tasks = np.random.rand(5, 10)
    optimal_agents = orchestrator.optimize_swarm(tasks)
    
    assert len(optimal_agents) <= 15  # 5 tasks x 3 agents
    assert all(a in orchestrator.agent_registry for a in optimal_agents)
