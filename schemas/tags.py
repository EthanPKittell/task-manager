from typing import TypedDict


class Tag(TypedDict):
    """A tag record.

    Attributes:
        id: The unique identifier for the tag.
        name: The tag's display name. Never empty.
    """

    id: int
    name: str
