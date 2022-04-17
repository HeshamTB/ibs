from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, OAuth2AuthorizationCodeBearer
from fastapi.security.api_key import APIKey
from sqlalchemy.orm import Session

from . import crud, models, schemas, auth_helper
from .database import SessionLocal, engine

from typing import List
from datetime import timedelta
import jwt

models.Base.metadata.create_all(bind=engine)
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="tkn")
oauth = OAuth2PasswordBearer(tokenUrl="tkn")

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
                           token: str = Depends(oauth),
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
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registerd")
        
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User, tags=['Users'])
def get_user_details(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

@app.get("/admin/users/", response_model=List[schemas.User], tags=['Admin'])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), api_key: APIKey = Depends(auth_helper.valid_api_key)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/admin/iotentities/", response_model=List[schemas.IotEntity], tags=['Admin'])
def read_iot_entities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), api_key: APIKey = Depends(auth_helper.valid_api_key)):
    iot_entities = crud.get_iot_entities(db, skip=skip, limit=limit)
    return iot_entities

# TODO: Can duplicate
@app.post("/admin/iotentities/create", response_model=schemas.IotEntity, tags=['Admin'])
def create_iot_entities(iot_entity: schemas.IotEntityCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(auth_helper.valid_api_key)):
    iot_entities = crud.create_iot_entity(db, iot_entity)
    return iot_entities

@app.get("/admin/users/{user_id}", response_model=schemas.User, tags=['Admin'])
def read_user(user_id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(auth_helper.valid_api_key)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# TODO: Can duplicate
@app.post("/admin/users/allowdevice/id", tags=['Admin'])
def allow_user_for_iot_entity_by_id(request: schemas.UserAllowForIotEntityRequestByID, db: Session = Depends(get_db), api_key: APIKey = Depends(auth_helper.valid_api_key)):
    user = crud.get_user(db, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    iot_entity = crud.get_iot_entity(db, request.iot_entity_id)
    if not iot_entity:
        raise HTTPException(status_code=404, detail="Iot Entity not found")

    res = crud.create_user_link_to_iot(db, request.user_id, request.iot_entity_id)
    if not res:
        raise HTTPException(status_code=500, detail="Could not complete operation")

    return user

@app.post("/admin/users/disallowdevice/id", tags=['Admin'])
def disallow_user_for_iot_entity_by_id(request: schemas.UserAllowForIotEntityRequestByID, db: Session = Depends(get_db), api_key: APIKey = Depends(auth_helper.valid_api_key)):
    user = crud.get_user(db, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    iot_entity = crud.get_iot_entity(db, request.iot_entity_id)
    if not iot_entity:
        raise HTTPException(status_code=404, detail="Iot Entity not found")

    #res = crud.create_user_link_to_iot(db, request.user_id, request.iot_entity_id)
    # Implement remove link
    if not res:
        raise HTTPException(status_code=500, detail="Could not complete operation")

    return

@app.post("/admin/users/allowdevice/name", tags=['Admin'])
def allow_user_for_iot_entity_by_name(request: schemas.UserAllowForIotEntityRequestByUsername, db: Session = Depends(get_db), api_key: APIKey = Depends(auth_helper.valid_api_key)):
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
def deactiveate_user(user_id: int, db:Session = Depends(get_db), api_key: APIKey = Depends(auth_helper.valid_api_key)):
    return

@app.post("/admin/users/{user_id}/activeate", tags=['Admin'])
def deactiveate_user(user_id: int, db:Session = Depends(get_db), api_key: APIKey = Depends(auth_helper.valid_api_key)):
    return

@app.post("/admin/iotdevice/gentoken/", response_model=schemas.Token, tags=['Admin'])
def generate_token_for_iot_device(bluetooth_mac : schemas.IotBluetoothMac, 
                                  api_key: APIKey = Depends(auth_helper.valid_api_key)):
    # We get here after a valid admin key, so send back permenant token
    data = {"bluetooth_mac": bluetooth_mac.bluetooth_mac}
    tkn = auth_helper.create_iot_dev_token(data)
    return {"access_token": tkn, "token_type": "bearer"}

@app.get("/users/acesslist/", response_model=List[schemas.IotEntity], tags=['Users'])
def get_iot_access_list_for_user(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    user = crud.get_user_by_username(db, current_user.username)
    return user.authorized_devices

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



