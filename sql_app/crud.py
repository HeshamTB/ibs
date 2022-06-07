# CRUD (Create, Read, Update, Delete) from db

from sqlalchemy import select, join
from sqlalchemy.orm import Session

from . import models, schemas, crypto, auth_helper

from datetime import datetime

# TODO: Data we can collect or log
#  - Last user connection (link to user)
#  - Last Iot Entity Connection (link to IotEntity)
#  - Any open request (link to user)
#  - Any polling from IotEntity? Maybe to much data

def get_user(db: Session, user_id: int) -> models.User:
    return db.query(models.User).get(user_id)

def get_iot_entity(db: Session, id: int):
    return db.query(models.IotEntity).get(id)

def get_iot_entity_by_description(db: Session, description: str):
    return db.query(models.IotEntity).filter(models.IotEntity.description == description).first()

def get_iot_entity_by_bluetooth_mac(db: Session, bluetooth_mac: str) -> models.IotEntity:
    return db.query(models.IotEntity).filter(models.IotEntity.bluetooth_mac == bluetooth_mac).first()

def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str) -> models.User:
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_access_log_for_door_by_door_mac(db: Session, bluetooth_mac : str):
    return db.query(models.DoorAccessLog).filter(models.DoorAccessLog.iot_dev_bluetooth_mac == bluetooth_mac).all()

def get_access_log_for_user_by_id(db: Session, id : str):
    return db.query(models.DoorAccessLog).filter(models.DoorAccessLog.user_id == id).all()

def get_room_data_now(db: Session) -> models.RoomSensorData:
    return db.query(models.RoomSensorData)[-1]

def create_user(db: Session, user: schemas.UserCreate):
    key = crypto.gen_new_key(user.password)
    salt = key[1]
    hashed_pass = key[0]
    db_user = models.User(email=user.email,
                          username=user.username,
                          hashed_password=hashed_pass,
                          passwd_salt=salt)
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
    link = db.query(models.UserAuthToIoTDev).filter(models.UserAuthToIoTDev.user_id == user_id).filter(models.UserAuthToIoTDev.iot_id == iot_dev_id).first()
    if link: return True
    new_link = models.UserAuthToIoTDev(user_id=user_id,
                                       iot_id=iot_dev_id,
                                       timestamp=datetime.now())
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return True

def remove_user_link_to_iot(db: Session, user_id: int, iot_dev_id: int):
    # Ensure link is not already present and it does not allow duplicates
    link = (db.query(models.UserAuthToIoTDev)
        .filter(models.UserAuthToIoTDev.user_id == user_id)
        .filter(models.UserAuthToIoTDev.iot_id == iot_dev_id)
        .first())
    if not link: return True
    db.delete(link)
    db.flush()
    db.commit()
    #db.refresh(link)
    return True

def set_open_door_request(db: Session, iot_entity_id: int, time_seconds : int):
    device = get_iot_entity(db, iot_entity_id)
    setattr(device, "open_request", True)
    if time_seconds < 1:
        time_seconds = 10 # Magic number move to global constant
    setattr(device, "time_seconds", time_seconds)
    db.add(device) 
    db.commit()
    db.refresh(device)
    return True

def set_close_door_request(db: Session, iot_id: int):
    device : models.IotEntity = get_iot_entity(db, iot_id)
    device.force_close = True
    db.add(device)
    db.commit()
    db.refresh(device)
    return True

def clear_close_door_request(db: Session, iot_id: int):
    device : models.IotEntity = get_iot_entity(db, iot_id)
    device.force_close = False
    db.add(device)
    db.commit()

def set_user_last_token(db: Session, username: str, token: str):
    user : models.User = get_user_by_username(db, username)
    user.last_token = token
    db.add(user)
    db.commit()
    db.refresh(user)
    return True

def get_user_last_token(db: Session, username: str):
    user : models.User = get_user_by_username(db, username)
    return user.last_token # This method is bad security practice.

def clear_open_door_request(db: Session, iot_entity_id: int):
    device = get_iot_entity(db, iot_entity_id)
    setattr(device, "open_request", False)
    setattr(device, "time_seconds", 10)
    db.add(device) 
    db.commit()
    db.refresh(device)
    return True

def record_door_access_log(db: Session, entry: schemas.DoorAccessLog):
    db_item = models.DoorAccessLog(user_id=entry.user_id,
                                iot_id=entry.iot_id,
                                command=entry.command,
                                timestamp=entry.timestamp)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

def record_room_sensor_data(db: Session, entry: schemas.IotMonitorRoomInfo):
    db_item = models.RoomSensorData(humidity=entry.humidity,
                                    people=entry.people,
                                    temperature=entry.temperature,
                                    smoke_sensor_reading=entry.smoke_sensor_reading,
                                    timestamp=datetime.now())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

def increment_door_access_list_counter(db: Session, iot_entity: models.IotEntity):
    iot_entity.acces_list_counter = iot_entity.acces_list_counter + 1
    db.add(iot_entity)
    db.commit()
    db.refresh(iot_entity)
