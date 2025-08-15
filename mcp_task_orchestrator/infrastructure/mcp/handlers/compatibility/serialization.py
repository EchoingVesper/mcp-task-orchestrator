"""
JSON serialization utilities and validation.

Ensures all data structures are JSON-serializable and handles common
conversion issues like datetime objects and enum types.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List
from enum import Enum

logger = logging.getLogger(__name__)


class SerializationValidator:
    """Ensures all data structures are JSON-serializable."""
    
    @staticmethod
    def validate_json_serializable(data: Any) -> Any:
        """Recursively validate and fix JSON serialization issues."""
        if data is None:
            return None
        elif isinstance(data, (str, int, float, bool)):
            return data
        elif isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, Enum):
            return data.value
        elif isinstance(data, dict):
            return {
                key: SerializationValidator.validate_json_serializable(value)
                for key, value in data.items()
            }
        elif isinstance(data, (list, tuple)):
            return [
                SerializationValidator.validate_json_serializable(item)
                for item in data
            ]
        else:
            # For any other type, convert to string
            logger.warning(f"Converting non-serializable type {type(data)} to string")
            return str(data)
    
    @staticmethod
    def convert_timestamps(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert all timestamp fields to ISO format strings."""
        timestamp_fields = [
            "created_at", "updated_at", "completed_at", "started_at", 
            "deleted_at", "cancelled_at", "due_date"
        ]
        
        result = data.copy()
        for field in timestamp_fields:
            if field in result and result[field] is not None:
                if isinstance(result[field], datetime):
                    result[field] = result[field].isoformat()
                elif isinstance(result[field], str):
                    # Already a string, ensure it's valid ISO format
                    try:
                        # Parse and re-format to ensure consistency
                        dt = datetime.fromisoformat(result[field].replace('Z', '+00:00'))
                        result[field] = dt.isoformat()
                    except (ValueError, AttributeError):
                        # If parsing fails, keep original string
                        pass
        
        return result
    
    @staticmethod
    def convert_enums(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert enum objects to their string values."""
        result = {}
        for key, value in data.items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, dict):
                result[key] = SerializationValidator.convert_enums(value)
            elif isinstance(value, list):
                result[key] = [
                    item.value if isinstance(item, Enum) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def test_serialization(data: Any) -> bool:
        """Test if data can be JSON serialized."""
        try:
            json.dumps(data)
            return True
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def ensure_serializable(data: Any) -> Any:
        """Ensure data is JSON-serializable, applying all conversions."""
        # Apply conversions in order
        if isinstance(data, dict):
            data = SerializationValidator.convert_timestamps(data)
            data = SerializationValidator.convert_enums(data)
        
        # Final validation and fixing
        data = SerializationValidator.validate_json_serializable(data)
        
        # Verify serialization works
        if not SerializationValidator.test_serialization(data):
            logger.error(f"Data still not serializable after conversion: {type(data)}")
            return {"error": "serialization_failed", "type": str(type(data))}
        
        return data