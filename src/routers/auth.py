from fastapi import APIRouter, HTTPException
from manocorp.fastapi.routing import SecFetchJsonRoute
from models.auth import (
    Auth,
    AuthPasswordSetMessage,
    AuthPasswordReset,
    AuthLoginResponse,
    AuthAuthentication,
)
from models.user import User
from sqlmodel import Session, create_engine, select
from helpers.jwt import encode_jwt_token
from helpers.auth import get_password_hash
import config


engine = create_engine(config.DATABASE_URL, echo=True)


router = APIRouter(route_class=SecFetchJsonRoute)

# Adding default headers for the API
ERROR_USER_INVALID_CREDS = HTTPException(status_code=422, detail="Invalid credentials")


@router.patch("/auth/password", response_model=AuthPasswordSetMessage)
def password_reset(auth: AuthPasswordReset):
    user_auth = None
    with Session(engine) as session:
        try:
            user = session.exec(
                select(User).where(
                    # ruff: noqa: E712
                    User.username == auth.username,
                    # ruff: noqa: E712
                ),
            ).first()

            if user:
                user_auth = session.exec(
                    select(Auth).where(
                        Auth.user_id == user.id,
                        Auth.reset_token == auth.reset_token,
                    ),
                ).first()

            else:
                raise HTTPException(
                    status_code=400,
                    detail="Something went wrong. Invalid link.",
                )

            if user_auth:
                if auth.new_password != auth.new_password_confirm:
                    raise HTTPException(
                        status_code=400,
                        detail="Passwords don't match.",
                    )
                else:
                    user_auth.password = user_auth.password_check(auth.new_password)
                    user_auth.reset_token = ""
                    # ruff: noqa: B105
                    session.add(user_auth)
                    session.commit()
                    session.refresh(user_auth)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Something went wrong. Invalid link.",
                )

            return AuthPasswordSetMessage(message="Your password has been set.")
        except Exception:
            raise HTTPException(status_code=400, detail="Unexpected Error")


@router.post("/auth/login", response_model=AuthLoginResponse)
def login(auth: AuthAuthentication):
    # Check if user exists
    with Session(engine) as session:
        user = session.exec(
            select(User).where(
                User.username == auth.username,
                User.is_active == True,
                User.deleted_at is None,
            ),
        ).first()
        if user:
            password = get_password_hash(auth.password)
            user_auth = session.exec(
                select(Auth).where(
                    Auth.user_id == user.id,
                    Auth.password == password,
                ),
            ).first()
            if user_auth:
                payload = {
                    "sub": str(user.id),
                    "username": user.username,
                }
                return AuthLoginResponse(access_token=encode_jwt_token(payload))
            else:
                raise ERROR_USER_INVALID_CREDS
        else:
            raise ERROR_USER_INVALID_CREDS
