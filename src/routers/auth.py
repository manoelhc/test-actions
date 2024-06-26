from fastapi import APIRouter, HTTPException
from manocorp.fastapi.routing import SecFetchJsonRoute
from sqlalchemy.exc import IntegrityError
from models.auth import Auth, AuthLogin, AuthAuthentication
from sqlmodel import Session, create_engine, select
import config


engine = create_engine(config.DATABASE_URL, echo=True)


router = APIRouter(route_class=SecFetchJsonRoute)

# Adding default headers for the API
ERROR_USER_INVALID_CREDS = HTTPException(status_code=422, detail="Invalid credentials")


@router.post("/auth/login", response_model=AuthAuthentication)
def auth_login(auth: AuthLogin):
    with Session(engine) as session:
        try:
            user = session.exec(
                select(Auth).where(
                    # ruff: noqa: E712
                    Auth.username == auth.username,
                    # ruff: noqa: E712
                    Auth.password == auth.password,
                    # ruff: noqa: E711
                    Auth.deleted_at == None,
                ),
            ).first()
            return AuthAuthentication.model_validate(user)
        except ValueError:
            raise ERROR_USER_INVALID_CREDS
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Unexpected Error")
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)
