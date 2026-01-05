"""
Pydantic Schema Utilities

Provides utilities for working with Pydantic models.

Usage:
    from shared_utils.schemas import to_json_schema, validate_json

    # Generate JSON schema
    schema = to_json_schema(MyModel)

    # Validate data
    instance = validate_json(MyModel, {"name": "John"})

    # Safe validation (returns None on failure)
    instance = validate_json_safe(MyModel, data)
"""

from shared_utils.schemas.pydantic import (
    to_json_schema,
    validate_json,
    validate_json_safe,
    model_to_dict,
    model_to_json,
    merge_models,
    create_partial_model,
)

__all__ = [
    "to_json_schema",
    "validate_json",
    "validate_json_safe",
    "model_to_dict",
    "model_to_json",
    "merge_models",
    "create_partial_model",
]
