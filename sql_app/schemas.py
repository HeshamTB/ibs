from typing import Any, List, Optional

from pydantic import BaseModel
from datetime import datetime


class IotEntityBase(BaseModel):
    bluetooth_mac: str
    description: str

class UserBase(BaseModel):
    email: str
    username: str

class IotEntityCreate(IotEntityBase):
    pass


class UserCreate(UserBase):
    password: str

class IotEntity(IotEntityBase):
    id: int
    description: str
    bluetooth_mac: str
    #authorized_users: List[User] = []
    open_request: bool # Flag to open
    class Config:
        orm_mode = True

class IotBluetoothMac(BaseModel):
    bluetooth_mac : str

class User(UserBase):
    id: int
    is_active: bool
    authorized_devices: List[IotEntity] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username : str
    # Token can conatin information. But we are already recording this in a database
    # for scalability. 

class UserAllowForIotEntityRequestByID(BaseModel):
    user_id: int
    iot_entity_id: int

class UserAllowForIotEntityRequestByUsername(BaseModel):
    username: str
    description: str

class OpenDoorRequestBase(BaseModel):
    username: str
    bluetooth_mac: str

class OpenDoorRequestTime(OpenDoorRequestBase):
    time_minutes: int

# Device sends this periodcally
class IotDoorPollingRequest(BaseModel):
    bluetooth_mac : str
    token : str
    class Config:
        orm_mode = True

class IotDoorPollingResponse(BaseModel):
    open_command : bool
    acces_list_counter : int

class IotMonitorRoomInfo(BaseModel):
    humidity : int
    people : int
    temperature : int
    smoke_sensor_reading : int
    token: str
    class Config:
        orm_mode = True

class IotMonitorRoomInfoTimestamped(IotMonitorRoomInfo):
    time: datetime
    class Config:
        orm_mode = True

class DoorAccessLog(BaseModel):
    user_id: int
    door_bluetooth_mac: str
    time: datetime
    class Config:
        orm_mode = True