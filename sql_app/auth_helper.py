# May 2022
# Hesham T. Banafa <hishaminv@gmail.com>

from typing import Optional
from decouple import config
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends, Security, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.api_key import APIKey, APIKeyHeader
from . import crud, crypto, schemas
import jwt

import time


JWT_SECRET = config('jwt_secret')
JWT_ALGO = config('jwt_algorithm')

__API_KEY = config('API_KEY')
__API_KEY_NAME = config('API_KEY_NAME')

api_key_header = APIKeyHeader(name=__API_KEY_NAME)

def create_access_token(data : dict, expires_delta : Optional[timedelta] = None):
    # TODO: Consider making non-expiring token
    to_encode = data.copy() # Since we may change the dict
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)
    return encoded_jwt

def authenticate_user(db: Session, username : str, password : str):
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    return crypto.verify_key(password, user.passwd_salt, user.hashed_password)

def valid_api_key(key = Security(api_key_header)):
    if not __API_KEY == key:
        raise HTTPException(401, detail="invalid key")
    return

def create_iot_dev_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)
    return encoded_jwt

def valid_iot_token(token : str, db: Session):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.DecodeError:
        return None

    mac_signed = payload.get("bluetooth_mac")
    device = crud.get_iot_entity_by_bluetooth_mac(db, mac_signed)
    return device

def valid_monitor_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.DecodeError:
        return None
    
    mac_signed = payload.get("bluetooth_mac")
    monitor = crud.get_monitor_bluetooth(db, mac_signed)
    return monitor
