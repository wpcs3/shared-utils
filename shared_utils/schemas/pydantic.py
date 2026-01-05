"""
Pydantic Schema Utilities

Provides utilities for working with Pydantic models.
"""

from typing import Any, Dict, Type, TypeVar, Optional, List
import json

T = TypeVar("T")


def to_json_schema(
    model: Type[Any],
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate JSON schema from a Pydantic model.

    Args:
        model: Pydantic model class
        title: Optional title override
        description: Optional description override

    Returns:
        JSON schema dict

    Usage:
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            age: int

        schema = to_json_schema(User)
    """
    schema = model.model_json_schema()

    if title:
        schema["title"] = title
    if description:
        schema["description"] = description

    return schema


def validate_json(
    model: Type[T],
    data: Any,
    strict: bool = False,
) -> T:
    """
    Validate JSON data against a Pydantic model.

    Args:
        model: Pydantic model class
        data: JSON data (dict or string)
        strict: If True, use strict validation

    Returns:
        Validated model instance

    Raises:
        ValidationError: If validation fails

    Usage:
        data = {"name": "John", "age": 30}
        user = validate_json(User, data)
    """
    if isinstance(data, str):
        data = json.loads(data)

    if strict:
        return model.model_validate(data, strict=True)
    return model.model_validate(data)


def validate_json_safe(
    model: Type[T],
    data: Any,
    default: Optional[T] = None,
) -> Optional[T]:
    """
    Validate JSON data, returning None (or default) on failure.

    Args:
        model: Pydantic model class
        data: JSON data (dict or string)
        default: Default value on validation failure

    Returns:
        Validated model instance or default
    """
    try:
        return validate_json(model, data)
    except Exception:
        return default


def model_to_dict(
    model: Any,
    exclude_none: bool = True,
    exclude_unset: bool = False,
    by_alias: bool = False,
) -> Dict[str, Any]:
    """
    Convert a Pydantic model to a dictionary.

    Args:
        model: Pydantic model instance
        exclude_none: Exclude None values
        exclude_unset: Exclude unset values
        by_alias: Use field aliases

    Returns:
        Dictionary representation
    """
    return model.model_dump(
        exclude_none=exclude_none,
        exclude_unset=exclude_unset,
        by_alias=by_alias,
    )


def model_to_json(
    model: Any,
    indent: Optional[int] = None,
    exclude_none: bool = True,
) -> str:
    """
    Convert a Pydantic model to JSON string.

    Args:
        model: Pydantic model instance
        indent: JSON indentation
        exclude_none: Exclude None values

    Returns:
        JSON string
    """
    return model.model_dump_json(
        indent=indent,
        exclude_none=exclude_none,
    )


def merge_models(
    base: T,
    update: Dict[str, Any],
    exclude_unset: bool = True,
) -> T:
    """
    Merge update dict into a Pydantic model, returning new instance.

    Args:
        base: Base model instance
        update: Dictionary of updates
        exclude_unset: Only apply set values from update

    Returns:
        New model instance with merged values

    Usage:
        user = User(name="John", age=30)
        updated = merge_models(user, {"age": 31})
    """
    base_data = base.model_dump()
    base_data.update(update)
    return type(base).model_validate(base_data)


def create_partial_model(
    model: Type[T],
    name: Optional[str] = None,
) -> Type[T]:
    """
    Create a version of a model where all fields are optional.

    Useful for PATCH endpoints where any field can be omitted.

    Args:
        model: Pydantic model class
        name: Optional name for the new model

    Returns:
        New model class with all optional fields

    Usage:
        class User(BaseModel):
            name: str
            age: int

        PartialUser = create_partial_model(User)
        # PartialUser has name: Optional[str] = None, age: Optional[int] = None
    """
    from typing import Optional as Opt
    from pydantic import create_model

    optional_fields = {
        field_name: (Opt[field_info.annotation], None)
        for field_name, field_info in model.model_fields.items()
    }

    return create_model(
        name or f"Partial{model.__name__}",
        **optional_fields,
    )
