
from . import crud, main, schemas, auth_helper
from decouple import config
from .database import SessionLocal
from datetime import timedelta

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
    iot_monitor = schemas.IotEntityCreate(bluetooth_mac="ff:ff:00:ff",
                                          description="Iot Lab Monitor")
    monitor_exists = crud.get_iot_entity_by_bluetooth_mac(db, iot_monitor.bluetooth_mac)
    if monitor_exists: return
    crud.create_iot_entity(db, iot_monitor)

def init_allowance():
    crud.create_user_link_to_iot(db, 1, 1)

def init():
    init_user()
    init_door()
    init_monitor()
    init_allowance()
    