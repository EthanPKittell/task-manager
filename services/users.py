from utils.errors import NotFoundError, ValidationError

NOTIFICATION_PREFS = ("email", "sms", "none")
DEFAULT_NOTIFICATION_PREF = "none"

USERS: dict[int, dict] = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "notification_pref": "none"},
    2: {"id": 2, "name": "Bob",   "email": "bob@example.com",   "notification_pref": "none"},
}

def get_user(user_id: int) -> dict:
    """Retrieve a user by ID.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user record as a dictionary.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    if user_id not in USERS:
        raise NotFoundError("User")
    return USERS[user_id]

def create_user(name: str, email: str) -> dict:
    """Create a new user.

    Args:
        name: The user's display name.
        email: The user's email address.

    Returns:
        The newly created user record.

    Raises:
        ValidationError: If name or email is empty.
    """
    if not name or not name.strip():
        raise ValidationError("name", "cannot be empty")
    if not email or "@" not in email:
        raise ValidationError("email", "must be a valid email address")
    new_id = max(USERS.keys()) + 1
    USERS[new_id] = {
        "id": new_id,
        "name": name,
        "email": email,
        "notification_pref": DEFAULT_NOTIFICATION_PREF,
    }
    return USERS[new_id]

def get_notification_pref(user_id: int) -> str:
    """Retrieve a user's notification preference.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user's notification preference, one of "email", "sms", or "none".

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    return get_user(user_id)["notification_pref"]

def update_notification_pref(user_id: int, pref: str) -> dict:
    """Update a user's notification preference.

    Args:
        user_id: The unique identifier for the user.
        pref: The new notification preference, one of "email", "sms", or "none".

    Returns:
        The updated user record as a dictionary.

    Raises:
        NotFoundError: If no user exists with the given ID.
        ValidationError: If pref is not one of "email", "sms", or "none".
    """
    user = get_user(user_id)
    if not isinstance(pref, str) or pref not in NOTIFICATION_PREFS:
        raise ValidationError("notification_pref", "must be one of: email, sms, none")
    user["notification_pref"] = pref
    return user

def list_users() -> list[dict]:
    """Retrieve all users.

    Args:
        None.

    Returns:
        A list of user records.

    Raises:
        None.
    """
    return list(USERS.values())
