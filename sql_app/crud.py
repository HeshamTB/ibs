# CRUD (Create, Read, Update, Delete) from db

from sqlalchemy.orm import Session

from . import models, schemas, crypto, auth_helper

# TODO: Data we can collect or log
#  - Last user connection (link to user)
#  - Last Iot Entity Connection (link to IotEntity)
#  - Any open request (link to user)
#  - Any polling from IotEntity? Maybe to much data

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_iot_entity(db: Session, id: int):
    return db.query(models.IotEntity).filter(models.IotEntity.id == id).first()

def get_iot_entity_by_description(db: Session, description: str):
    return db.query(models.IotEntity).filter(models.IotEntity.description == description).first()

def get_iot_entity_by_bluetooth_mac(db: Session, bluetooth_mac: str):
    return db.query(models.IotEntity).filter(models.IotEntity.bluetooth_mac == bluetooth_mac).first()

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
    db_user = models.User(email=user.email, username=user.username,hashed_password=hashed_pass, passwd_salt=salt)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_iot_entities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.IotEntity).offset(skip).limit(limit).all()


def create_iot_entity(db: Session, iot_entity: schemas.IotEntityCreate):
    db_item = models.IotEntity(bluetooth_mac=iot_entity.bluetooth_mac,
                               description=iot_entity.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_user_link_to_iot(db: Session, user_id: int, iot_dev_id: int):
    # Ensure link is not already present and it does not allow duplicates
    new_link = models.UserAuthToIoTDev(user_id=user_id, iot_entity_id=iot_dev_id)
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return True

def set_open_door_request(db: Session, iot_entity_id: int):
    device = get_iot_entity(db, iot_entity_id)
    setattr(device, "open_request", True)
    db.add(device) 
    db.commit()
    db.refresh(device)
    return True