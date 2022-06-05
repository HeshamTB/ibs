from typing import Any, List, Optional

from pydantic import BaseModel
from datetime import datetime


class IotEntityBase(BaseModel):
    # Common attributes for all Iot devices
    room_id: int  # Used to link with sensors and other devices
    bluetooth_mac: str
    description: str

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    # For when creating users (needs password once to store)
    password: str

class IotDoor(IotEntityBase):
    id: int # Door ID
    open_request: bool # Standing flag to open
    time_seconds: int  # Used when open request
    force_close: bool  # Force a close mid timed open request
    is_open: bool
    accesslist_counter: int
    class Config:
        orm_mode = True

class IotDoorPollingRequest(BaseModel):
    bluetooth_mac: str
    token: str

class IotMonitor(IotEntityBase):
    # Info of room monitor and current readings
    id: int
    room_id: int
    people: int
    temp_c: int
    smoke: int
    humidity: int    
    class Config:
        orm_mode = True

class IotMonitorRoomInfo(BaseModel):
    humidity : int
    people : int
    temperature : int
    smoke : int
    token: str

class IotDoorCreate(IotEntityBase):
    room_id: int

class IotMonitorCreate(IotEntityBase):
    room_id: int


class Room(BaseModel):
    id: int
    building_name: str
    building_number: int
    class Config:
        orm_mode = True

class RoomCreate(BaseModel):
    building_name: str
    building_number: int

class IotBluetoothMac(BaseModel):
    bluetooth_mac : str

class User(UserBase):
    id: int
    is_active: bool
    authorized_rooms: List[Room] = [] # TODO: Change to auth rooms not devs
    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

class UserTokenData(BaseModel):
    username: str

class IotDeviceTokenData(BaseModel):
    bluetooth_mac: str

class DoorAccessLog(BaseModel):
    user_id: int
    room_id: int
    timestamp: datetime
    #token: str


class IotMonitorRoomEntry(BaseModel):
    humidity : int
    people : int
    temperature : int
    smoke: int
    token: str
    class Config:
        orm_mode = True

class AllowRoomAccessRequestID(BaseModel):
    user_id: int
    room_id: int

class AllowRoomAccessRequestName(BaseModel):
    username: str
    description: int

class UserRoomAccessLogRequest(BaseModel):
    username: str

class RoomAccessLogRequest(BaseModel):
    room_id: int

class RoomAccessLogRequestUserID(BaseModel):
    room_id: int
    user_id: int

class RoomAccessLogRequestUserUsername(BaseModel):
    username: str
    room_id: int

class OpenRoomRequest(BaseModel):
    user_id: int
    room_id: int
    time_seconds: int

# class UserAllowForIotEntityRequestByID(BaseModel):
#     user_id: int
#     iot_entity_id: int

# class UserAllowForIotEntityRequestByUsername(BaseModel):
#     username: str
#     description: str

# class OpenDoorRequestBase(BaseModel):
#     username: str
#     bluetooth_mac: str

# class OpenDoorRequestTime(OpenDoorRequestBase):
#     time_seconds: int

# # Device sends this periodcally
# class IotDoorPollingRequest(BaseModel):
#     bluetooth_mac : str
#     token : str
#     class Config:
#         orm_mode = True

# class IotDoorPollingResponse(BaseModel):
#     open_command : bool
#     acces_list_counter : int
#     time_seconds : int

# class IotMonitorRoomInfo(BaseModel):
#     humidity : int
#     people : int
#     temperature : int
#     smoke_sensor_reading : int
#     token: str
#     class Config:
#         orm_mode = True

# class IotMonitorRoomInfoTimestamped(IotMonitorRoomInfo):
#     time: datetime
#     class Config:
#         orm_mode = True

# class DoorAccessLog(BaseModel):
#     user_id: int
#     door_bluetooth_mac: str
#     time: datetime
#     class Config:
#         orm_mode = True

# class AccessLogRequest(BaseModel):
#     bluetooth_mac : str

# class UserAccessLogRequestUsername(BaseModel):
#     username : str

# class UserAccessLogRequestEmail(BaseModel):
#     email : str

# class UserAccessLogRequestID(BaseModel):
#     id : int
