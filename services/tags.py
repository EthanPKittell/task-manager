from schemas.tags import Tag
from utils.errors import ValidationError

TAGS: dict[int, Tag] = {
    1: {"id": 1, "name": "urgent"},
    2: {"id": 2, "name": "home"},
}

def create_tag(data: dict) -> Tag:
    """Create a new tag.

    Args:
        data: The request body. Must be a dict with a non-empty string "name".

    Returns:
        The newly created tag record.

    Raises:
        ValidationError: If data is not a dict, or name is missing, empty, or
            not a string.
    """
    if not isinstance(data, dict):
        raise ValidationError("tag", "body must be a JSON object")
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("name", "cannot be empty")
    new_id = max(TAGS.keys()) + 1
    TAGS[new_id] = {"id": new_id, "name": name}
    return TAGS[new_id]
