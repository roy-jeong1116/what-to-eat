from passlib.context import CryptContext
from sqlalchemy.orm import Session
from domain.user.user_schema import UserCreate, UserDelete
from models import User
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user_create: UserCreate):
    db_user = User(username=user_create.username,
                   login_id=user_create.login_id,
                   password=pwd_context.hash(user_create.password1),
                   )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_existing_username(db: Session, user_create: UserCreate):
    return db.query(User).filter(User.username == user_create.username).first()

def get_existing_login_id(db: Session, user_create: UserCreate):
    return db.query(User).filter(User.login_id == user_create.login_id).first()

def delete_user(db: Session, user_id: int, password: str):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    if not pwd_context.verify(password, user.password):  # noqa
        raise ValueError("비밀번호가 일치하지 않습니다.")

    db.delete(user)
    db.commit()

    return True

def get_user_by_login_id(db: Session, login_id: str):
    return db.query(User).filter(User.login_id == login_id).first()