# orbital-agent/src/agent_management/agent_lifecycle.py
import logging
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class AgentStatus:
    last_heartbeat: datetime
    resource_usage: dict
    active: bool = True
    retry_count: int = 0

class AgentLifecycleManager:
    def __init__(self, swarm_coordinator, check_interval: int = 30):
        self.agents: Dict[str, AgentStatus] = {}
        self.swarm = swarm_coordinator
        self.check_interval = check_interval
        self.lock = threading.Lock()
        self.monitor_thread: Optional[threading.Thread] = None
        self.running = False

    def register_agent(self, agent_id: str, initial_resources: dict):
        with self.lock:
            self.agents[agent_id] = AgentStatus(
                last_heartbeat=datetime.utcnow(),
                resource_usage=initial_resources
            )
        logger.info(f"Registered new agent: {agent_id}")

    def update_heartbeat(self, agent_id: str, metrics: dict):
        with self.lock:
            if agent_id in self.agents:
                self.agents[agent_id].last_heartbeat = datetime.utcnow()
                self.agents[agent_id].resource_usage = metrics
                self.agents[agent_id].retry_count = 0
                logger.debug(f"Heartbeat updated for agent: {agent_id}")

    def start_monitoring(self):
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Started agent lifecycle monitoring")

    def _monitor_loop(self):
        while self.running:
            try:
                self._check_agent_health()
                self._cleanup_inactive_agents()
                self._recover_failed_agents()
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
            time.sleep(self.check_interval)

    def _check_agent_health(self):
        threshold = datetime.utcnow() - timedelta(
            seconds=self.check_interval * 3)
        
        with self.lock:
            for agent_id, status in self.agents.items():
                if status.last_heartbeat < threshold:
                    status.retry_count += 1
                    logger.warning(f"Agent {agent_id} missed heartbeat")
                    
                    if status.retry_count > 2:
                        status.active = False
                        self._handle_agent_failure(agent_id)

    def _cleanup_inactive_agents(self):
        with self.lock:
            inactive_agents = [
                aid for aid, status in self.agents.items() 
                if not status.active
            ]
            
            for agent_id in inactive_agents:
                del self.agents[agent_id]
                logger.info(f"Cleaned up inactive agent: {agent_id}")

    def _recover_failed_agents(self):
        with self.lock:
            failed_agents = [
                aid for aid, status in self.agents.items()
                if not status.active and status.retry_count <= 5
            ]
            
            for agent_id in failed_agents:
                logger.info(f"Attempting recovery for agent: {agent_id}")
                if self._restart_agent(agent_id):
                    self.agents[agent_id].active = True
                    self.agents[agent_id].retry_count = 0

    def _handle_agent_failure(self, agent_id: str):
        logger.error(f"Critical failure detected for agent: {agent_id}")
        self.swarm.redistribute_tasks(agent_id)
        
    def _restart_agent(self, agent_id: str) -> bool:
        try:
            logger.info(f"Restarting agent: {agent_id}")
            # Implementation would connect to orchestration system
            # to restart the failed agent instance
            return True
        except Exception as e:
            logger.error(f"Agent restart failed: {str(e)}")
            return False<i class="fl-spin"></i>
