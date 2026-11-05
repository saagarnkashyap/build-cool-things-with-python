"""Generate passwords with operating-system-backed randomness."""

import secrets
import string

SYMBOLS = "!@#$%^&*()-_=+"
DEFAULT_GROUPS = (string.ascii_lowercase, string.ascii_uppercase, string.digits, SYMBOLS)


def generate_password(length: int = 16, groups: tuple[str, ...] = DEFAULT_GROUPS) -> str:
    """Sample uniformly, accepting only passwords containing every selected group."""
    if not groups or any(not group for group in groups):
        raise ValueError("Choose at least one nonempty character group.")
    if not max(4, len(groups)) <= length <= 128:
        raise ValueError("Length must be 4-128 and allow a character from every group.")
    alphabet = "".join(dict.fromkeys("".join(groups)))
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if all(any(character in group for character in password) for group in groups):
            return password


def generate_passwords(length: int = 16, count: int = 1,
                       groups: tuple[str, ...] = DEFAULT_GROUPS) -> list[str]:
    """Create a validated batch for the desktop interface."""
    if not 1 <= count <= 20:
        raise ValueError("Choose between 1 and 20 passwords.")
    return [generate_password(length, groups) for _ in range(count)]
