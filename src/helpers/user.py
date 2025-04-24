from email_validator import validate_email as ev_validate_email
import re


def validate_user(username: str) -> str:
    # TODO: https://github.com/shouldbee/reserved-usernames/blob/master/reserved-usernames.txt
    if len(username) <= 2:
        raise ValueError("Username should be more than 2 characters")
    elif len(username) >= 255:
        raise ValueError("Username should be less than 255 characters")
    if re.match(r"^[a-z0-9.-_]+$", username) is None:
        raise ValueError("Username must be alphanumeric, underscore and dots only")
    elif username.find("[deleted]") > 0:
        raise ValueError("Username must be alphanumeric, underscore and dots only")
    return username


def validate_email(email: str) -> str:
    try:
        return ev_validate_email(
            email,
            allow_quoted_local=False,
            dns_resolver=None,
        ).normalized
    except Exception:
        raise ValueError("Email format is invalid.")
