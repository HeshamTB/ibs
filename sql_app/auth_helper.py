
from typing import Optional
from decouple import config
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import crud, crypto, schemas
import jwt

import time


JWT_SECRET = config('jwt_secret')
JWT_ALGO = config('jwt_algorithm')



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

