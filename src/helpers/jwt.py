import config
import jwt


def encode_jwt_token(data: dict):
    return jwt.encode(data, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def decode_jwt_token(token: str):
    return jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
