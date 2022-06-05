from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, OAuth2AuthorizationCodeBearer
from fastapi.security.api_key import APIKey
from sqlalchemy.orm import Session

from . import crud, models, schemas, auth_helper
from .database import SessionLocal, engine

from typing import List
from datetime import timedelta, datetime
import jwt

models.Base.metadata.create_all(bind=engine)
oauth = OAuth2PasswordBearer(tokenUrl="tkn")

app = FastAPI(title="IoT Building System")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})

inactive_user_exception = HTTPException(status_code=status.HTTP_403_FORBIDDEN,
        detail="Inactive user")

email_used_exception = HTTPException(status_code=400, 
        detail="Email already registered")

username_used_exception = HTTPException(status_code=400,
        detail="Username already registerd")

user_not_found_exception = HTTPException(status_code=404,
        detail="User not found")

room_not_found_exception = HTTPException(status_code=404,
        detail="Room not found")

unauth_to_open = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                  detail="Unauthrized to open")

str_not_implemented = 'Not Implemented'

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth_helper.JWT_SECRET, algorithms=[auth_helper.JWT_ALGO])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        #token_data = schemas.TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise inactive_user_exception
    return current_user

@app.post("/users/reg", response_model=schemas.User, tags=['Users'])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise email_used_exception

    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise username_used_exception
        
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User, tags=['Users'])
def get_user_details(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

@app.get("/admin/users/", response_model=List[schemas.User], tags=['Admin'])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/admin/doors/", response_model=List[schemas.IotDoor], tags=['Admin'])
def read_iot_doors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    doors = crud.get_doors(db, skip=skip, limit=limit)
    return doors

@app.get("/admin/monitors/", response_model=List[schemas.IotMonitor], tags=['Admin'])
def read_iot_doors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    monitors = crud.get_monitors(db, skip=skip, limit=limit)
    return monitors

@app.get("/admin/rooms/", response_model=List[schemas.Room], tags=['Admin'])
def read_iot_doors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = crud.get_rooms(db, skip=skip, limit=limit)
    return rooms

@app.post("/admin/create/door/", response_model=schemas.IotDoor, tags=['Admin'])
def create_iot_entities(door: schemas.IotDoorCreate, db: Session = Depends(get_db)):
    #iot_entities = crud.create_iot_entity(db, iot_entity)
    new_door = crud.create_door(db, door)
    return new_door

@app.post("/admin/create/monitor/", response_model=schemas.IotMonitor, tags=['Admin'])
def create_iot_entities(monitor: schemas.IotMonitorCreate, db: Session = Depends(get_db)):
    #iot_entities = crud.create_iot_entity(db, iot_entity)
    new_monitor = crud.create_monitor(db, monitor)
    return new_monitor

@app.post("/admin/create/room/", response_model=schemas.Room, tags=['Admin'])
def create_iot_entities(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    new_room = crud.create_room(db, room)
    return new_room

@app.get("/admin/users/{user_id}", response_model=schemas.User, tags=['Admin'])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise user_not_found_exception
    return db_user

@app.post("/admin/users/allowaccess/id", response_model=schemas.AllowRoomAccessRequestID, tags=['Admin'])
def allow_user_room_access_by_id(request: schemas.AllowRoomAccessRequestID,
                                    db: Session = Depends(get_db)):
    user = crud.get_user(db, request.user_id)
    if not user:
        raise user_not_found_exception

    room = crud.get_room(db, request.room_id)
    if not room:
        raise room_not_found_exception

    #res = crud.create_user_link_to_iot(db, request.user_id, request.iot_entity_id)
    res = crud.allow_user_room_access(db, request.user_id, request.room_id)
    if not res:
        raise HTTPException(status_code=500, detail="Could not complete operation")

    return request

@app.post("/admin/users/disallowaccess/id", tags=['Admin'])
def disallow_user_room_access_by_id(request: schemas.AllowRoomAccessRequestID,
                                        db: Session = Depends(get_db)):
    user = crud.get_user(db, request.user_id)
    if not user:
        raise user_not_found_exception

    room = crud.get_room(db, request.room_id)
    if not room:
        raise room_not_found_exception

    res = crud.disallow_user_room_access(db, request.user_id, request.room_id)
    if not res:
        raise HTTPException(status_code=500, detail="Could not complete operation")

    return

@app.post("/admin/users/{user_id}/deactiveate", tags=['Admin'], description=str_not_implemented)
def deactiveate_user(user_id: int, db:Session = Depends(get_db)):
    return

@app.post("/admin/users/{user_id}/activeate", tags=['Admin'], description=str_not_implemented)
def deactiveate_user(user_id: int, db:Session = Depends(get_db)):
    return

@app.post("/admin/iotdevice/gentoken/", response_model=schemas.Token, tags=['Admin'])
def generate_token_for_iot_device(bluetooth_mac : schemas.IotBluetoothMac, 
                                  api_key: APIKey = Depends(auth_helper.valid_api_key)):
    # We get here after a valid admin key, so send back permenant token
    data = {"bluetooth_mac": bluetooth_mac.bluetooth_mac}
    tkn = auth_helper.create_iot_dev_token(data)
    return {"access_token": tkn, "token_type": "bearer"}

@app.post("/admin/room/accesslog/", tags=['Admin'])
def get_access_log_for_door(request : schemas.RoomAccessLogRequest,
                            db : Session = Depends(get_db)):
    room = crud.get_room(db, request.room_id)
    if not room: raise room_not_found_exception
    return crud.get_access_log_for_room(db, request.room_id)

@app.post("/admin/room/authrizedusers/", tags=['Admin'])
def get_room_authrized_users(room: schemas.Room,
                            db: Session = Depends(get_db)):
    room: models.Room = crud.get_room(db, room_id=room.id)
    return room.authorized_users

@app.post("/admin/user/accesslog/room/", tags=['Admin'])
def get_room_access_log_history_for_user(request : schemas.RoomAccessLogRequestUserID,
                                    db : Session = Depends(get_db)):
    user = crud.get_user(db, request.user_id)
    if not user: raise user_not_found_exception
    room = crud.get_room(db, request.room_id)
    if not room: raise room_not_found_exception
    return crud.get_room_access_log_for_user(db, request.user_id, request.room_id)

@app.post("/admin/user/accesslog/room/username", tags=['Admin'])
def get_room_access_log_history_for_user_by_username(request : schemas.RoomAccessLogRequestUserUsername,
                                    db : Session = Depends(get_db)):
    user = crud.get_user_by_username(db, request.username)
    if not user: raise user_not_found_exception
    return crud.get_room_access_log_for_user(db, user.id, request.room_id)

@app.get("/users/acesslist/", response_model=List[schemas.Room], tags=['Users'])
def get_room_access_list_for_user(db: Session = Depends(get_db),
                                  current_user: models.User = Depends(get_current_active_user)):

    # Can use the ORM method current_user.authrized_rooms pulls from database on demand...
    return current_user.authorized_rooms

@app.get("/admin/roominfo/now/", response_model=schemas.IotMonitor, tags=['Admin'])
def get_room_data(room : schemas.Room,
                  db: Session = Depends(get_db)):
    monitor = crud.get_room_current_readings(db, room)
    return monitor

@app.get("/admin/roominfo/now/all", response_model=List[schemas.IotMonitor], tags=['Admin'])
def get_all_rooms_data(db: Session = Depends(get_db)):
    monitors = crud.get_monitors(db)
    return monitors

@app.post("/users/open", tags=['Users'])
def issue_open_door_command(request: schemas.OpenRoomRequest, 
                            db: Session = Depends(get_db),
                            current_user: schemas.User = Depends(get_current_active_user)):

    #device = crud.open_door_request(db, request.room_id, request.time_seconds)
    #if not device: raise unauth_to_open # To no leak info
    user : models.User = crud.get_user(db, current_user.id)
    log_entry = schemas.DoorAccessLog(user_id=current_user.id,
                                      room_id=request.room_id,
                                      timestamp=datetime.now())
    res = crud.open_door_request(db, request=request)
    if not res: raise unauth_to_open
    crud.record_door_access_log(db, log_entry)
    return

@app.post("/users/tkn", response_model=schemas.Token, tags=['Users'])
@app.post("/tkn", response_model=schemas.Token, tags=['Users'])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_helper.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    #access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_helper.create_access_token(
        data={"sub": form_data.username}, expires_delta=timedelta(minutes=15)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/iotdevice/door/status", response_model=schemas.IotDoor, tags=['Iot'])
def polling_method_for_door(request: schemas.IotDoorPollingRequest,
                                  db: Session = Depends(get_db)):

    device: models.IotDoor = auth_helper.valid_iot_door_token(request.token, db)
    if not device: 
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials")
    room : models.Room = crud.get_room_from_door(db, device)
    # Reset open_request to False
    #crud.clear_open_door_request(db, room_id=room.id) # Make response object to perserve values;
    return device

@app.post("/iotdevice/monitor/status", tags=['Iot'])
def polling_method_for_room_monitor(request: schemas.IotMonitorRoomInfo,
                                    db: Session = Depends(get_db)):
    device : schemas.IotMonitor = auth_helper.valid_iot_monitor_token(request.token, db)
    if not device:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials")
    crud.record_room_sensor_data(db, request)
    return request