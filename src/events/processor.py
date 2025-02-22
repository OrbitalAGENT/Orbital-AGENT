# orbital-agent/src/events/processor.py
import asyncio
from dataclasses import dataclass
from typing import Callable, Dict

@dataclass
class Event:
    type: str
    payload: dict

class EventProcessor:
    def __init__(self):
        self.handlers: Dict[str, Callable[[Event], None]] = {}
        self.queue = asyncio.Queue()
        
    def register_handler(self, event_type: str, handler: Callable[[Event], None]):
        self.handlers[event_type] = handler
        
    async def publish(self, event: Event):
        await self.queue.put(event)
        
    async def start_processing(self):
        while True:
            event = await self.queue.get()
            if handler := self.handlers.get(event.type):
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error handling event {event.type}: {str(e)}")
            self.queue.task_done()
