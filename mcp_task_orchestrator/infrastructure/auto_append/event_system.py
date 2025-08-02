"""
Auto-Append Event System

Event-driven task creation system that triggers on task lifecycle events
(creation, completion, failure, status changes) and enables rule-based
automatic task generation.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events that can trigger auto-append rules."""
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_CANCELLED = "task_cancelled"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_ASSIGNED = "task_assigned"
    TASK_DEADLINE_APPROACHING = "task_deadline_approaching"
    TASK_OVERDUE = "task_overdue"
    MILESTONE_REACHED = "milestone_reached"
    ERROR_THRESHOLD_EXCEEDED = "error_threshold_exceeded"


@dataclass
class TaskEvent:
    """Represents an event in the task lifecycle."""
    event_type: EventType
    task_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_data: Dict[str, Any] = field(default_factory=dict)
    source: str = "task_orchestrator"
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_type": self.event_type.value,
            "task_id": self.task_id,
            "timestamp": self.timestamp.isoformat(),
            "event_data": self.event_data,
            "source": self.source,
            "correlation_id": self.correlation_id
        }


class EventListener(ABC):
    """Abstract base class for event listeners."""
    
    @abstractmethod
    async def handle_event(self, event: TaskEvent) -> None:
        """Handle a task event."""
        pass
    
    @abstractmethod
    def get_supported_events(self) -> Set[EventType]:
        """Return set of event types this listener handles."""
        pass


class EventBus:
    """
    Event bus for publishing and subscribing to task events.
    
    Provides centralized event distribution with support for:
    - Async event handling
    - Multiple listeners per event type
    - Event filtering and routing
    - Error handling and recovery
    """
    
    def __init__(self):
        self._listeners: Dict[EventType, List[EventListener]] = {}
        self._event_history: List[TaskEvent] = []
        self._max_history_size = 1000
        self._processing_events = False
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._background_task: Optional[asyncio.Task] = None
        
    def subscribe(self, listener: EventListener) -> None:
        """Subscribe an event listener to relevant events."""
        supported_events = listener.get_supported_events()
        
        for event_type in supported_events:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            
            if listener not in self._listeners[event_type]:
                self._listeners[event_type].append(listener)
                logger.debug(f"Subscribed listener {listener.__class__.__name__} to {event_type.value}")
    
    def unsubscribe(self, listener: EventListener) -> None:
        """Unsubscribe an event listener from all events."""
        for event_type in list(self._listeners.keys()):
            if listener in self._listeners[event_type]:
                self._listeners[event_type].remove(listener)
                logger.debug(f"Unsubscribed listener {listener.__class__.__name__} from {event_type.value}")
    
    async def publish(self, event: TaskEvent) -> None:
        """Publish an event to all relevant listeners."""
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
        
        # Queue event for processing
        await self._event_queue.put(event)
        
        # Start background processing if not already running
        if not self._background_task or self._background_task.done():
            self._background_task = asyncio.create_task(self._process_events())
    
    async def _process_events(self) -> None:
        """Background task to process events from the queue."""
        self._processing_events = True
        
        try:
            while not self._event_queue.empty():
                try:
                    event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                    await self._handle_event(event)
                    self._event_queue.task_done()
                except asyncio.TimeoutError:
                    break
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
        finally:
            self._processing_events = False
    
    async def _handle_event(self, event: TaskEvent) -> None:
        """Handle a single event by notifying all relevant listeners."""
        listeners = self._listeners.get(event.event_type, [])
        
        if not listeners:
            logger.debug(f"No listeners for event type {event.event_type.value}")
            return
        
        logger.info(f"Processing event {event.event_type.value} for task {event.task_id}")
        
        # Handle events concurrently
        tasks = []
        for listener in listeners:
            task = asyncio.create_task(self._safe_handle_listener(listener, event))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_handle_listener(self, listener: EventListener, event: TaskEvent) -> None:
        """Safely handle event for a single listener with error recovery."""
        try:
            await listener.handle_event(event)
            logger.debug(f"Listener {listener.__class__.__name__} handled event {event.event_type.value}")
        except Exception as e:
            logger.error(f"Listener {listener.__class__.__name__} failed to handle event "
                        f"{event.event_type.value}: {e}")
    
    def get_event_history(self, 
                         event_type: Optional[EventType] = None,
                         task_id: Optional[str] = None,
                         limit: int = 100) -> List[TaskEvent]:
        """Get event history with optional filtering."""
        events = self._event_history[-limit:]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if task_id:
            events = [e for e in events if e.task_id == task_id]
        
        return events
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        event_counts = {}
        for event in self._event_history:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "total_events": len(self._event_history),
            "event_counts": event_counts,
            "active_listeners": sum(len(listeners) for listeners in self._listeners.values()),
            "processing_events": self._processing_events,
            "queue_size": self._event_queue.qsize()
        }


class TaskEventPublisher:
    """
    Publisher for task lifecycle events.
    
    Integrates with the task orchestration system to automatically
    publish events when tasks change state.
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
    
    async def publish_task_created(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Publish task created event."""
        event = TaskEvent(
            event_type=EventType.TASK_CREATED,
            task_id=task_id,
            event_data={
                "title": task_data.get("title"),
                "task_type": task_data.get("task_type"),
                "specialist_type": task_data.get("specialist_type"),
                "complexity": task_data.get("complexity"),
                "parent_task_id": task_data.get("parent_task_id")
            }
        )
        await self.event_bus.publish(event)
    
    async def publish_task_completed(self, task_id: str, completion_data: Dict[str, Any]) -> None:
        """Publish task completed event."""
        event = TaskEvent(
            event_type=EventType.TASK_COMPLETED,
            task_id=task_id,
            event_data={
                "completion_summary": completion_data.get("summary"),
                "artifacts": completion_data.get("artifacts", []),
                "next_action": completion_data.get("next_action"),
                "duration_minutes": completion_data.get("duration_minutes")
            }
        )
        await self.event_bus.publish(event)
    
    async def publish_task_failed(self, task_id: str, failure_data: Dict[str, Any]) -> None:
        """Publish task failed event."""
        event = TaskEvent(
            event_type=EventType.TASK_FAILED,
            task_id=task_id,
            event_data={
                "error_message": failure_data.get("error_message"),
                "error_type": failure_data.get("error_type"),
                "retry_count": failure_data.get("retry_count", 0),
                "recovery_suggestions": failure_data.get("recovery_suggestions", [])
            }
        )
        await self.event_bus.publish(event)
    
    async def publish_task_status_changed(self, task_id: str, 
                                        old_status: str, new_status: str,
                                        additional_data: Dict[str, Any] = None) -> None:
        """Publish task status change event."""
        event = TaskEvent(
            event_type=EventType.TASK_STATUS_CHANGED,
            task_id=task_id,
            event_data={
                "old_status": old_status,
                "new_status": new_status,
                **(additional_data or {})
            }
        )
        await self.event_bus.publish(event)
    
    async def publish_milestone_reached(self, task_id: str, milestone_data: Dict[str, Any]) -> None:
        """Publish milestone reached event."""
        event = TaskEvent(
            event_type=EventType.MILESTONE_REACHED,
            task_id=task_id,
            event_data={
                "milestone_name": milestone_data.get("milestone_name"),
                "completion_percentage": milestone_data.get("completion_percentage"),
                "milestone_type": milestone_data.get("milestone_type"),
                "achievements": milestone_data.get("achievements", [])
            }
        )
        await self.event_bus.publish(event)


# Global event bus instance
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def get_event_publisher() -> TaskEventPublisher:
    """Get a task event publisher using the global event bus."""
    return TaskEventPublisher(get_event_bus())