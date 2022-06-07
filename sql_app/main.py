from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, OAuth2AuthorizationCodeBearer
from fastapi.security.api_key import APIKey
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas, auth_helper, init_db
from .database import SessionLocal, engine
from .utils import get_db

from typing import List
from datetime import timedelta, datetime
import jwt

models.Base.metadata.create_all(bind=engine)
oauth = OAuth2PasswordBearer(tokenUrl="tkn")

app = FastAPI(title="IoT Building System")

# Split into endpoints modules
#app.include_router(users.router,prefix="/users", tags=["User"])
init_db.init()


def get_current_user(token: str = Depends(oauth), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth_helper.JWT_SECRET, algorithms=[auth_helper.JWT_ALGO])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_iot_device(current_device: schemas.IotBluetoothMac = Depends(),
                           db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = jwt.decode(token, auth_helper.JWT_SECRET, algorithms=[auth_helper.JWT_ALGO])
    mac_signed = payload.get("bluetooth_mac")
    if (mac_signed != current_device): raise credentials_exception
    device = crud.get_iot_entity_by_bluetooth_mac(db, mac_signed)
    return device

@app.post("/users/reg", response_model=schemas.User, tags=['Users'])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email/Username already registered")

    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Email/Username already registered")
    
    db_user = crud.create_user(db=db, user=user)
    if not db_user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    access_token = auth_helper.create_access_token(
        data={"sub": db_user.username}, expires_delta=timedelta(minutes=15)
    )
    crud.set_user_last_token(db, db_user.username, access_token)

    return db_user 

@app.get("/users/me/", response_model=schemas.User, tags=['Users'])
def get_user_details(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

@app.post("/users/open", tags=['Users'])
def issue_open_door_command(command: schemas.OpenDoorRequestTime, 
                            db: Session = Depends(get_db),
                            current_user: schemas.User = Depends(get_current_active_user)):
    err = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                  detail="Unauthrized to open")
    device = crud.get_iot_entity_by_bluetooth_mac(db, command.bluetooth_mac)
    if not device: raise err
    # TODO: Use database search rather then this linear search
    user = crud.get_user(db, current_user.id)
    for dev in user.authorized_devices:
        if dev.bluetooth_mac == device.bluetooth_mac:
            crud.set_open_door_request(db, device.id, command.time_seconds)
            log_entry = schemas.DoorAccessLog(user_id=current_user.id,
                                             iot_id=device.id,
                                             command="OPEN",
                                             timestamp=datetime.now())
            crud.record_door_access_log(db, log_entry)
            return device
    raise err

@app.post("/users/close", tags=['Users'])
def issue_close_door_command(command: schemas.CloseDoorRequest,
                             db: Session = Depends(get_db),
                             current_user: schemas.User = Depends(get_current_active_user)):
    err = HTTPException(status.HTTP_401_UNAUTHORIZED,
            detail="Unaithrized to close")
    device = crud.get_iot_entity_by_bluetooth_mac(db, command.bluetooth_mac)
    if not device: raise err
    user = crud.get_user(db, current_user.id)
    for dev in user.authorized_devices:
        if dev.bluetooth_mac == device.bluetooth_mac:
            crud.set_close_door_request(db, device.id)
            log_entry = schemas.DoorAccessLog(user_id=current_user.id,
                                             iot_id=device.id,
                                             command="CLOSE",
                                             timestamp=datetime.now())
            crud.record_door_access_log(db, log_entry)
            return device

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
    crud.set_user_last_token(db, form_data.username, access_token)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/acesslist/", response_model=List[schemas.RoomOverview], tags=['Users'])
def get_iot_access_list_for_user(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    user = crud.get_user_by_username(db, current_user.username)
    access_list = list()
    for device in user.authorized_devices:
        dev_db : models.IotEntity = device
        sensors = crud.get_room_data_now(db)
        if not sensors: raise HTTPException(status_code=500, detail="No Room link")
        entry : schemas.RoomOverview = schemas.RoomOverview(
            id=dev_db.id,
            description=dev_db.description,
            bluetooth_mac=dev_db.bluetooth_mac,
            open_request=dev_db.open_request,
            time_seconds=dev_db.time_seconds,
            acces_list_counter=dev_db.acces_list_counter,
            humidity=sensors.humidity,
            people=sensors.people,
            temperature=sensors.temperature,
            smoke_sensor_reading=sensors.smoke_sensor_reading
        )
        access_list.append(entry)
    return access_list

@app.get("/admin/users/", response_model=List[schemas.User], tags=['Admin'])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/admin/iotentities/", response_model=List[schemas.IotEntity], tags=['Admin'])
def read_iot_entities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    iot_entities = crud.get_iot_entities(db, skip=skip, limit=limit)
    return iot_entities

# TODO: Can duplicate
@app.post("/admin/iotentities/create", response_model=schemas.IotEntity, tags=['Admin'])
def create_iot_entities(iot_entity: schemas.IotEntityCreate, db: Session = Depends(get_db)):
    iot_entities = crud.create_iot_entity(db, iot_entity)
    return iot_entities

@app.get("/admin/users/{user_id}", response_model=schemas.User, tags=['Admin'])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/admin/users/allowdevice/id", tags=['Admin'])
def allow_user_for_iot_entity_by_id(request: schemas.UserAllowForIotEntityRequestByID, db: Session = Depends(get_db)):
    user = crud.get_user(db, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    iot_entity = crud.get_iot_entity(db, request.iot_entity_id)
    if not iot_entity:
        raise HTTPException(status_code=404, detail="Iot Entity not found")

    res = crud.create_user_link_to_iot(db, request.user_id, request.iot_entity_id)
    if not res:
        raise HTTPException(status_code=500, detail="Could not complete operation")

    crud.increment_door_access_list_counter(db, iot_entity)
    return

@app.post("/admin/users/disallowdevice/id", tags=['Admin'])
def disallow_user_for_iot_entity_by_id(request: schemas.UserAllowForIotEntityRequestByID, db: Session = Depends(get_db)):
    user = crud.get_user(db, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    iot_entity = crud.get_iot_entity(db, request.iot_entity_id)
    if not iot_entity:
        raise HTTPException(status_code=404, detail="Iot Entity not found")

    res = crud.remove_user_link_to_iot(db, request.user_id, request.iot_entity_id)
    if not res:
        raise HTTPException(status_code=500, detail="Could not complete operation")
    
    crud.increment_door_access_list_counter(db, iot_entity)
    return

@app.post("/admin/users/allowdevice/name", tags=['Admin'])
def allow_user_for_iot_entity_by_name(request: schemas.UserAllowForIotEntityRequestByUsername, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    iot_entity = crud.get_iot_entity_by_description(db, request.description)
    if not iot_entity:
        raise HTTPException(status_code=404, detail="Iot Entity not found")

    res = crud.create_user_link_to_iot(db, user.id, iot_entity.id)
    if not res:
        raise HTTPException(status_code=500, detail="Could not complete operation")

    return

@app.post("/admin/users/{user_id}/deactiveate", tags=['Admin'])
def deactiveate_user(user_id: int, db:Session = Depends(get_db)):
    return

@app.post("/admin/users/{user_id}/activeate", tags=['Admin'])
def deactiveate_user(user_id: int, db:Session = Depends(get_db)):
    return

@app.post("/admin/iotdevice/gentoken/", response_model=schemas.Token, tags=['Admin'])
def generate_token_for_iot_device(bluetooth_mac : schemas.IotBluetoothMac, 
                                  api_key: APIKey = Depends(auth_helper.valid_api_key)):
    # We get here after a valid admin key, so send back permenant token
    data = {"bluetooth_mac": bluetooth_mac.bluetooth_mac}
    tkn = auth_helper.create_iot_dev_token(data)
    return {"access_token": tkn, "token_type": "bearer"}

@app.post("/admin/iotdevice/accesslog/", tags=['Admin'])
def get_access_log_for_door(request : schemas.AccessLogRequest,
                            db : Session = Depends(get_db)):
    device = crud.get_iot_entity_by_bluetooth_mac(db, request.bluetooth_mac)
    if not device: raise HTTPException(status_code=404, detail="Iot Entity not found")
    return crud.get_access_log_for_door_by_door_mac(db, request.bluetooth_mac)

@app.post("/admin/user/accesslog/email/", tags=['Admin'])
def get_access_log_history_for_user(request : schemas.UserAccessLogRequestEmail,
                                    db : Session = Depends(get_db)):
    user = crud.get_user_by_email(db, request.email)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return crud.get_access_log_for_user_by_id(db, user.id)

@app.post("/admin/user/accesslog/username/", tags=['Admin'])
def get_access_log_history_for_user(request : schemas.UserAccessLogRequestUsername,
                                    db : Session = Depends(get_db)):
    user = crud.get_user_by_username(db, request.username)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return crud.get_access_log_for_user_by_id(db, user.id)

@app.get("/admin/roominfo/now/", tags=['Admin'])
def get_room_data(db: Session = Depends(get_db)):
    return crud.get_room_data_now(db)

@app.post("/iotdevice/door/status", response_model=schemas.IotDoorPollingResponse, tags=['Iot'])
def polling_method_for_iot_entity(request: schemas.IotDoorPollingRequest,
                                  db: Session = Depends(get_db)):

    device: models.IotEntity = auth_helper.valid_iot_token(request.token, db)
    if not device: 
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials")
    
    response : schemas.IotDoorPollingResponse = schemas.IotDoorPollingResponse(
                                                open_command=device.open_request,
                                                acces_list_counter=0,
                                                time_seconds=device.time_seconds,
                                                force_close=device.force_close)
    # Reset open_request to False
    crud.clear_open_door_request(db, device.id)
    crud.clear_close_door_request(db, device.id)
    return response

@app.post("/iotdevice/monitor/status", tags=['Iot'])
def polling_method_for_room_monitor(request: schemas.IotMonitorRoomInfo,
                                    db: Session = Depends(get_db)):
    device : schemas.IotEntity = auth_helper.valid_iot_token(request.token, db)
    if not device:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials")
    crud.record_room_sensor_data(db, request)
    return request

@app.post("/iotdevice/door/users", response_class=PlainTextResponse, tags=['Iot'])
def get_allowed_usernames(request: schemas.IotDoorPollingRequest,
                          db: Session = Depends(get_db)):

    iot_door = crud.get_iot_entity_by_bluetooth_mac(db, request.bluetooth_mac)
    if not iot_door: 
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials")
    usernames = str()
    for user in iot_door.authorized_users:
        db_user : models.User = user
        usernames = usernames + db_user.username + '\n'
    
    return usernames

@app.post("/iotdevice/door/tkns", response_class=PlainTextResponse, tags=['Iot'])
def get_allowed_usernames(request: schemas.IotDoorPollingRequest,
                          db: Session = Depends(get_db)):

    iot_door = crud.get_iot_entity_by_bluetooth_mac(db, request.bluetooth_mac)
    if not iot_door: 
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials")
    tkns = str()
    for user in iot_door.authorized_users:
        db_user : models.User = user
        tkns = tkns + db_user.last_token + '\n'
    
    return tkns