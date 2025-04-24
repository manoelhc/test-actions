import config
import string
import secrets

from blake3 import blake3
from base64 import b64encode


def get_password_hash(passwd: str) -> str:
    hasher = blake3()
    hasher.update(bytearray(passwd.encode("utf-8")))
    hasher.update(bytearray(config.PASSWORD_SALT.encode("utf-8")))
    return str(b64encode(hasher.digest())[:43])


def get_password_token(length=44) -> str:
    chars = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(chars) for _ in range(length))
    hasher = blake3()
    hasher.update(bytearray(password.encode("utf-8")))
    hasher.update(bytearray(config.PASSWORD_SALT.encode("utf-8")))
    return str(b64encode(hasher.digest())[:43])


def password_generator(length=44) -> str:
    chars = string.ascii_letters + string.digits + "@$!%*?&"
    return "".join(secrets.choice(chars) for _ in range(length))
