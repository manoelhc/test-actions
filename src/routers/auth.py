from fastapi import APIRouter, HTTPException
from manocorp.fastapi.routing import SecFetchJsonRoute
from sqlalchemy.exc import IntegrityError
from models.auth import Auth, AuthPasswordSetMessage, AuthPasswordReset
from models.user import User
from sqlmodel import Session, create_engine, select
import config


engine = create_engine(config.DATABASE_URL, echo=True)


router = APIRouter(route_class=SecFetchJsonRoute)

# Adding default headers for the API
ERROR_USER_INVALID_CREDS = HTTPException(status_code=422, detail="Invalid credentials")


@router.patch("/auth/password", response_model=AuthPasswordSetMessage)
def password_reset(auth: AuthPasswordReset):
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
                raise ValueError("Something went wrong. Invalid link.")

            if user_auth:
                if auth.new_password != auth.new_password_confirm:
                    raise ValueError("Passwords don't match.")
                else:
                    user_auth.password = auth.new_password
                    user_auth.model_validate(user_auth)
                    # ruff: noqa: B105
                    user_auth.reset_token = ""
                    session.add(user_auth)
                    session.commit()
            else:
                raise ValueError("Something went wrong. Invalid link.")
            return AuthPasswordSetMessage(message="Your password has been set.")
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Unexpected Error")
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)
