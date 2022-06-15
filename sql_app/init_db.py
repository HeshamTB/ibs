# June 2022
# Hesham T. Banafa <hishaminv@gmail.com>

from . import crud, main, schemas, auth_helper
from decouple import config
from .database import SessionLocal
from datetime import timedelta, datetime
from random import randint

db = SessionLocal()

def init_user():
    user = schemas.UserCreate(email="hisham@banafa.com.sa",
                            username="Hesham",
                            password=config('first_user_pass'))
    user_exists = crud.get_user_by_email(db, user.email)
    if user_exists: return
    crud.create_user(db, user)
    token = auth_helper.create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=15))
    res = crud.set_user_last_token(db, user.username, token)

    user_exists = None
    user = schemas.UserCreate(email="osama@mail.none",
                            username="Osama",
                            password=config('first_user_pass'))
    user_exists = crud.get_user_by_email(db, user.email)
    if user_exists: return
    crud.create_user(db, user)
    token = auth_helper.create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=15))
    res = crud.set_user_last_token(db, user.username, token)

    user_exists = None
    user = schemas.UserCreate(email="Hussain@mail.none",
                            username="Hussain",
                            password=config('first_user_pass'))
    user_exists = crud.get_user_by_email(db, user.email)
    if user_exists: return
    crud.create_user(db, user)
    token = auth_helper.create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=15))
    res = crud.set_user_last_token(db, user.username, token)

    user_exists = None
    user = schemas.UserCreate(email="Assad@mail.none",
                            username="Assad",
                            password=config('first_user_pass'))
    user_exists = crud.get_user_by_email(db, user.email)
    if user_exists: return
    crud.create_user(db, user)
    token = auth_helper.create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=15))
    res = crud.set_user_last_token(db, user.username, token)

def init_door():
    iot_door = schemas.IotEntityCreate(bluetooth_mac="94:b9:7e:fb:57:1a",
                                       description="Iot Lab Door")
    door_exists = crud.get_iot_entity_by_bluetooth_mac(db, iot_door.bluetooth_mac)
    if door_exists: return
    crud.create_iot_entity(db, iot_door)

def init_monitor():
    iot_monitor = schemas.IotEntityCreate(bluetooth_mac="ff:ff:ff",
                                          description="Iot Lab Monitor")
    monitor_exists = crud.get_monitor_bluetooth(db, iot_monitor.bluetooth_mac)
    if monitor_exists: return
    crud.create_monitor(db, iot_monitor)

def init_allowance():
    crud.create_user_link_to_iot(db, 1, 1)

def init_sensor_data():
    monitor = crud.get_monitor(db, 1)
    if monitor.sensor_history: return
    for i in range(50):
        room_data = \
            schemas.\
            IotMonitorRoomInfo\
                (humidity=randint(20, 80),
                people=randint(0, 10),
                temperature=randint(18, 27),
                smoke_sensor_reading=randint(150, 700),
                token='dummy')
        crud.record_room_sensor_data(db, room_data, monitor)
    
def init_open_close_requests():
    user = crud.get_user_by_email(db, "hisham@banafa.com.sa")
    if user.access_log: return
    crud.set_open_door_request(db, 1, 10)
    log_entry = schemas.DoorAccessLog(user_id=user.id,
                                             iot_id=1,
                                             command="OPEN",
                                             timestamp=datetime.now())
    crud.record_door_access_log(db, log_entry)

    log_entry = schemas.DoorAccessLog(user_id=user.id,
                                             iot_id=1,
                                             command="OPEN",
                                             timestamp=datetime.now())
    crud.record_door_access_log(db, log_entry)

    log_entry = schemas.DoorAccessLog(user_id=user.id,
                                                iot_id=1,
                                                command="OPEN",
                                                timestamp=datetime.now())
    crud.record_door_access_log(db, log_entry)


    log_entry = schemas.DoorAccessLog(user_id=user.id,
                                             iot_id=1,
                                             command="CLOSE",
                                             timestamp=datetime.now())
    crud.record_door_access_log(db, log_entry)

def init_user_connections():
    users = [ crud.get_user(db, 1),
              crud.get_user(db, 2),
              crud.get_user(db, 3)]
    
    for i in range(3):
        crud.record_user_connection(db, users[i], datetime.now())
        crud.record_user_connection(db, users[i], datetime.now())
        crud.record_user_connection(db, users[i], datetime.now())

def init_link_room_monitor():
    monitor = crud.get_monitor(db, 1)
    door = crud.get_iot_entity(db, 1)
    monitor.door = door
    crud.update_monitor(db, monitor)
    
def init():
    init_user()
    init_door()
    init_monitor()
    init_allowance()
    init_sensor_data()
    init_open_close_requests()
    init_user_connections()
    init_link_room_monitor()
    
