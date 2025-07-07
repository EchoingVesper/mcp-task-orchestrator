"""
Time-related value objects.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass(frozen=True)
class Duration:
    """Value object representing a duration of time."""
    seconds: float
    
    def __post_init__(self):
        if self.seconds < 0:
            raise ValueError("Duration cannot be negative")
    
    @classmethod
    def from_minutes(cls, minutes: float) -> 'Duration':
        """Create duration from minutes."""
        return cls(seconds=minutes * 60)
    
    @classmethod
    def from_hours(cls, hours: float) -> 'Duration':
        """Create duration from hours."""
        return cls(seconds=hours * 3600)
    
    @classmethod
    def from_timedelta(cls, td: timedelta) -> 'Duration':
        """Create duration from timedelta."""
        return cls(seconds=td.total_seconds())
    
    @property
    def minutes(self) -> float:
        """Get duration in minutes."""
        return self.seconds / 60
    
    @property
    def hours(self) -> float:
        """Get duration in hours."""
        return self.seconds / 3600
    
    @property
    def as_timedelta(self) -> timedelta:
        """Convert to timedelta."""
        return timedelta(seconds=self.seconds)
    
    def __add__(self, other: 'Duration') -> 'Duration':
        """Add two durations."""
        if not isinstance(other, Duration):
            return NotImplemented
        return Duration(self.seconds + other.seconds)
    
    def __sub__(self, other: 'Duration') -> 'Duration':
        """Subtract durations."""
        if not isinstance(other, Duration):
            return NotImplemented
        result = self.seconds - other.seconds
        if result < 0:
            raise ValueError("Resulting duration cannot be negative")
        return Duration(result)
    
    def __str__(self) -> str:
        """Format duration as human-readable string."""
        if self.seconds < 60:
            return f"{self.seconds:.1f}s"
        elif self.seconds < 3600:
            return f"{self.minutes:.1f}m"
        elif self.seconds < 86400:
            return f"{self.hours:.1f}h"
        else:
            days = self.seconds / 86400
            return f"{days:.1f}d"


@dataclass(frozen=True)
class TimeWindow:
    """Value object representing a time window."""
    start: datetime
    end: datetime
    
    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError("End time must be after start time")
    
    @classmethod
    def from_start_and_duration(cls, start: datetime, duration: Duration) -> 'TimeWindow':
        """Create time window from start time and duration."""
        return cls(start=start, end=start + duration.as_timedelta)
    
    @classmethod
    def from_now_with_duration(cls, duration: Duration) -> 'TimeWindow':
        """Create time window starting now with given duration."""
        now = datetime.utcnow()
        return cls(start=now, end=now + duration.as_timedelta)
    
    @property
    def duration(self) -> Duration:
        """Get duration of the time window."""
        return Duration.from_timedelta(self.end - self.start)
    
    def contains(self, timestamp: datetime) -> bool:
        """Check if timestamp is within the window."""
        return self.start <= timestamp <= self.end
    
    def overlaps(self, other: 'TimeWindow') -> bool:
        """Check if this window overlaps with another."""
        return self.start < other.end and other.start < self.end
    
    def extend(self, duration: Duration) -> 'TimeWindow':
        """Create new window extended by duration."""
        return TimeWindow(self.start, self.end + duration.as_timedelta)
    
    def shift(self, duration: Duration) -> 'TimeWindow':
        """Create new window shifted by duration."""
        td = duration.as_timedelta
        return TimeWindow(self.start + td, self.end + td)
    
    def __str__(self) -> str:
        """Format time window as string."""
        return f"{self.start.isoformat()} - {self.end.isoformat()}"


@dataclass(frozen=True)
class TimeEstimate:
    """Value object for time estimates with confidence."""
    best_case: Duration
    expected: Duration
    worst_case: Duration
    confidence: float  # 0.0 to 1.0
    
    def __post_init__(self):
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        if self.best_case.seconds > self.expected.seconds:
            raise ValueError("Best case cannot be longer than expected")
        
        if self.expected.seconds > self.worst_case.seconds:
            raise ValueError("Expected cannot be longer than worst case")
    
    @property
    def range(self) -> Duration:
        """Get range between best and worst case."""
        return Duration(self.worst_case.seconds - self.best_case.seconds)
    
    @property
    def variance_ratio(self) -> float:
        """Get ratio of range to expected (measure of uncertainty)."""
        if self.expected.seconds == 0:
            return 0.0
        return self.range.seconds / self.expected.seconds