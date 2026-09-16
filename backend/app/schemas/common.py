"""
Base Schema Utilities and Common Response Models (Stage A).
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """
    Base Pydantic model enforcing camelCase wire serialization and deserialization
    while maintaining standard snake_case naming in internal Python code.
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        serialize_by_alias=True,
    )


T = TypeVar("T")


class PaginatedResponse(CamelModel, Generic[T]):
    """
    Generic paginated list envelope required by PRD 00:
    {
      "items": [...],
      "nextCursor": null | string,
      "hasMore": bool
    }
    """
    items: List[T]
    next_cursor: Optional[str] = None
    has_more: bool = False
