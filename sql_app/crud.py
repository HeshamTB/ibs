# CRUD (Create, Read, Update, Delete) from db

from sqlalchemy.orm import Session

from . import models, schemas, crypto, auth_helper

from datetime import datetime

# TODO: Data we can collect or log
#  - Any open request (link to user)

def get_user(db: Session, user_id: int):
    return db.query(models.User).get(user_id)

def get_door_by_id(door_id: int):
    return db.query(models.IotDoor).get(door_id)

def get_door_by_description(db: Session, description: str):
    # TODO: 2 or more Desciptions may collide 
    return db.query(models.IotDoor).filter(models.IotDoor.description == description).first()

def get_door_by_bluetooth_mac(db: Session, bluetooth_mac: str):
    return db.query(models.IotDoor).filter(models.IotDoor.bluetooth_mac == bluetooth_mac).first()

def get_monitor_by_bluetooth_mac(db: Session, bluetooth_mac: str):
    return db.query(models.IotMonitor).filter(models.IotMonitor.bluetooth_mac == bluetooth_mac).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_access_log_for_room(db: Session, room_id: int):
    return db.query(models.DoorAccessLog).filter(models.DoorAccessLog.room == room_id).all()

def get_access_log_for_user_by_id(db: Session, id : str):
    return db.query(models.DoorAccessLog).filter(models.DoorAccessLog.user_id == id).all()

def get_room_data_now(db: Session, room_id: int):
    return db.query(models.IotMonitor).filter(models.IotMonitor.room_id == room_id)

def get_doors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.IotDoor).offset(skip).limit(limit).all()

def get_monitors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.IotMonitor).offset(skip).limit(limit).all()

def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Room).offset(skip).limit(limit).all()

def get_user_room_access_list_by_username(db: Session, username: str):
    user : models.User = get_user_by_username(db, username)
    links : List[models.UserRoomAuth] = db.query(models.UserRoomAuth).filter(models.UserRoomAuth.user_id == user.id).all()

    return db.query(models.Room).filter(models.Room.authorized_users == user.id).all()

def get_room_door(db: Session, room_id: int):
    door = db.query(models.IotDoor).filter(models.IotDoor.room_id == room_id).first()
    return door

def get_room(db: Session, room_id: int):
    room = db.query(models.Room).get(room_id)
    return room

def get_room_access_log_for_user(db: Session, user_id: int, room_id: int):
    log = db.query(models.DoorAccessLog).filter(models.DoorAccessLog.user_id == user_id, models.DoorAccessLog.room == room_id).all()
    return log

def get_room_current_readings(db: Session, room: schemas.Room) -> models.IotMonitor:
    room : models.Room = get_room(db, room.id)
    monitor = db.query(models.IotMonitor).filter(models.IotMonitor.room_id == room.id).first()
    return mon

def get_monitor_for_room(db: Session, room: schemas.Room) -> models.IotMonitor:
    return db.query(models.IotMonitor).filter(models.IotMonitor.room_id == room.id).first()

def get_door_for_room(db: Session, room_id: int) -> models.IotDoor:
    return db.query(models.IotDoor).filter(models.IotDoor.room_id == room_id).first()

def get_room_from_door(db: Session, door: models.IotDoor):
    return get_room(db, door.room_id)


def create_user(db: Session, user: schemas.UserCreate):
    key = crypto.gen_new_key(user.password)
    salt = key[1]
    hashed_pass = key[0]
    db_user = models.User(email=user.email, username=user.username,hashed_password=hashed_pass, passwd_salt=salt)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_door(db: Session, door: schemas.IotDoorCreate):
    db_item = models.IotDoor(room_id=door.room_id,
                            description=door.description,
                            bluetooth_mac=door.bluetooth_mac)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_monitor(db: Session, monitor: schemas.IotMonitorCreate):
    db_item = models.IotMonitor(room_id=monitor.room_id,
                                description=monitor.description,
                                bluetooth_mac=monitor.bluetooth_mac)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return 

def create_room(db: Session, room: schemas.RoomCreate):
    db_item = models.Room(building_name=room.building_name,
                          building_number=room.building_number)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def allow_user_room_access(db: Session, user_id: int, room_id: int):
    link = db.query(models.UserRoomAuth).filter(models.UserRoomAuth.user_id == user_id, models.UserRoomAuth.room_id == room_id).first()
    if link: return link
    new_link = models.UserRoomAuth(user_id=user_id, room_id=room_id)
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return link

def disallow_user_room_access(db: Session, user_id, room_id: int):
    link = db.query(models.UserRoomAuth).filter(models.UserRoomAuth.user_id == user_id, models.UserRoomAuth.room_id == room_id)
    if not link: return True
    db.delete(link)
    db.flush()
    db.commit()
    return True

def open_door_request(db: Session, request: schemas.OpenRoomRequest, time_seconds: int = 10):
    link = db.query(models.UserRoomAuth).filter(models.UserRoomAuth.user_id == request.user_id,
                                                models.UserRoomAuth.room_id == request.room_id).first()
    if not link: return False
    door : models.IotDoor = db.query(models.IotDoor).filter(models.IotDoor.room_id == request.room_id).first()
    if not door: return False
    setattr(door, "open_request", True)
    if time_seconds < 1:
        time_seconds = 10 # Magic number move to global constant
    setattr(door, "time_seconds", time_seconds)
    db.add(door) 
    db.commit()
    db.refresh(door)
    return True

def clear_open_door_request(db: Session, room_id: int):
    door : models.IotDoor = db.query(models.IotDoor).filter(models.IotDoor.room_id == room_id).first()
    setattr(door, "open_request", False)
    setattr(door, "time_seconds", 10)
    db.add(door) 
    db.commit()
    db.refresh(door)
    return True

def record_door_access_log(db: Session, entry: schemas.DoorAccessLog):
    db_item = models.DoorAccessLog(user_id=entry.user_id,
                                room=entry.room_id,
                                timestamp=entry.timestamp)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

def record_room_sensor_data(db: Session, entry: schemas.IotMonitorRoomInfo):
    db_item = models.RoomSensorData(humidity=entry.humidity,
                                    people=entry.people,
                                    temperature=entry.temperature,
                                    smoke=entry.smoke,
                                    timestamp=datetime.now())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

def on_access_list_change(db: Session, room_id: int, allow: bool):
    # Use when a user is allowed or disallowed to a room.
    door = get_door_for_room(db, room_id)
    door.accesslist_counter = door.accesslist_counter + 1
    db.add(door) 
    db.commit()
    db.refresh(door)

# TODO: Get room sensor data
# TODO: Get room door status