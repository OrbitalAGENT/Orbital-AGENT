# src/automation/auto_remediator.py
import logging
from typing import Callable, Dict

class RemediationAction:
    def __init__(self, name: str, condition: Callable[[], bool], action: Callable[[], None]):
        self.name = name
        self.condition = condition
        self.action = action
        
class AutoRemediator:
    def __init__(self):
        self.actions: Dict[str, RemediationAction] = {}
        
    def register_action(self, action: RemediationAction) -> None:
        self.actions[action.name] = action
        
    def monitor(self) -> None:
        for name, action in self.actions.items():
            try:
                if action.condition():
                    logging.info(f"Executing remediation action: {name}")
                    action.action()
            except Exception as e:
                logging.error(f"Remediation failed for {name}: {str(e)}")
