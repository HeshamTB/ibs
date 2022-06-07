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
    time_seconds: int
    force_close: bool
    acces_list_counter: int
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
    time_seconds: int

class CloseDoorRequest(OpenDoorRequestBase):
    pass
# Device sends this periodcally
class IotDoorPollingRequest(BaseModel):
    bluetooth_mac : str
    token : str
    class Config:
        orm_mode = True

class IotDoorPollingResponse(BaseModel):
    open_command : bool
    acces_list_counter : int
    time_seconds : int
    force_close: bool

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
    iot_id: str
    command: str
    timestamp: datetime
    class Config:
        orm_mode = True

class AccessLogRequest(BaseModel):
    bluetooth_mac : str

class UserAccessLogRequestUsername(BaseModel):
    username : str

class UserAccessLogRequestEmail(BaseModel):
    email : str

class UserAccessLogRequestID(BaseModel):
    id : int

class RoomOverview(IotEntity):
    humidity : int
    people : int
    temperature : int
    smoke_sensor_reading : int
