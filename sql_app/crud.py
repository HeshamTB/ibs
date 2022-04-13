# CRUD (Create, Read, Update, Delete) from db

from sqlalchemy.orm import Session

from . import models, schemas, crypto, auth_helper


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    key = crypto.gen_new_key(user.password)
    salt = key[1]
    hashed_pass = key[0]
    # TODO: check if user already exists? based on name,email ...
    db_user = models.User(email=user.email, username=user.username,hashed_password=hashed_pass, passwd_salt=salt)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_iot_entities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.IotEntity).offset(skip).limit(limit).all()


def create_iot_entity(db: Session, item: schemas.IotEntityCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
