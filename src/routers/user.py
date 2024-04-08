from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from models.user import User, UserSimple, UserCreate, UserUpdate
from sqlmodel import Session, create_engine, select
import config
from datetime import datetime


engine = create_engine(config.DATABASE_URL, echo=True)
router = APIRouter()

ERROR_USER_NOT_CHANGED = HTTPException(
    status_code=400,
    detail="User has not being changed",
)
ERROR_USER_ALREADY_EXISTS = HTTPException(status_code=400, detail="User already exists")
ERROR_USER_INVALID_USERNAME = HTTPException(status_code=422, detail="Invalid username")
ERROR_USER_NOT_FOUND = HTTPException(status_code=404, detail="User not found")
ERROR_BAD_REQUEST = HTTPException(status_code=400, detail="Bad request")


@router.post("/user", response_model=UserSimple)
def create_user(user: UserCreate):
    with Session(engine) as session:
        try:
            user = User(username=user.username)
            user.model_validate(user)
            session.add(user)
            session.commit()
            # session.refresh(user)
            return UserSimple.model_validate(user)
        except ValueError:
            raise ERROR_USER_INVALID_USERNAME
        except IntegrityError:
            raise HTTPException(status_code=400, detail="User already exists")
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)


@router.get("/users/{page}", response_model=list[UserSimple])
def read_all_user(page: int = 1):
    with Session(engine) as session:
        users = session.exec(
            select(User)
            .where(
                # ruff: noqa: E712
                User.is_active == True,
                # ruff: noqa: E711
                User.deleted_at == None,
            )
            .order_by(User.username.asc())
            .offset((page - 1) * 20)
            .limit(20),
        )
        return [UserSimple.model_validate(user) for user in users]


@router.get("/user/{username}", response_model=UserSimple)
def read_user(username: str):
    with Session(engine) as session:
        try:
            user = session.exec(
                select(User).where(
                    User.username == username,
                    # ruff: noqa: E712
                    User.is_active == True,
                    # ruff: noqa: E711
                    User.deleted_at == None,
                ),
            ).first()
            return UserSimple.model_validate(user)
        except Exception as _:
            raise ERROR_USER_NOT_FOUND


@router.put("/user", response_model=UserSimple)
def update_user(user_request: UserUpdate):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_request.id)).first()
        try:
            # Check the new username is already taken
            if user.username != user_request.username:
                if session.exec(
                    select(User).where(User.username == user_request.username),
                ).first():
                    raise ERROR_USER_ALREADY_EXISTS

            user.username = user_request.username
            user.model_validate(user)
            user.updated_at = datetime.now()
            user.is_active = user_request.is_active
            session.add(user)
            session.commit()
            return UserSimple.model_validate(user)
        except ValueError:
            raise ERROR_USER_INVALID_USERNAME
        except IntegrityError:
            raise ERROR_USER_ALREADY_EXISTS


@router.delete("/user/{username}", response_model=UserSimple)
def delete_user(username: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if user is None:
            raise ERROR_USER_NOT_FOUND
        user.is_active = False
        user.username = f"{user.username}[deleted]"
        user.deleted_at = datetime.now()
        session.add(user)
        session.commit()
        return UserSimple.model_validate(user)
