import config
import jwt


def encode_jwt_token(data: dict):
    return jwt.encode(data, config.SECRET_KEY, algorithm=config.ALGORITHM)


def decode_jwt_token(token: str):
    return jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
