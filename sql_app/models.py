from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    passwd_salt = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    authorized_rooms = relationship("Room", secondary= 'user_room_link', lazy='dynamic')

class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True, index=True)
    #door_id = Column(Integer, ForeignKey('iot_doors.id'))
    building_name = Column(String(512))
    building_number = Column(Integer)

    authorized_users = relationship("User", secondary='user_room_link')

class UserRoomAuth(Base):
    __tablename__ = 'user_room_link'

    user_id = Column(Integer, ForeignKey('user_accounts.id'), primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey('rooms.id'), primary_key=True, index=True)

class IotMonitor(Base):
    __tablename__ = 'iot_monitors'

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    temp_c = Column(Integer, default=0)
    smoke = Column(Integer, default=0)
    humidity = Column(Integer, default=0)
    people = Column(Integer, default=0)
    description = Column(String(512))
    bluetooth_mac = Column(String(512))

class IotDoor(Base):
    __tablename__ = 'iot_doors'

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    open_request = Column(Boolean, default=False)
    time_seconds = Column(Integer, default=10)
    is_open = Column(Boolean, default=False)
    force_close = Column(Boolean, default=False)
    accesslist_counter = Column(Integer, default=0)
    description = Column(String(512))
    bluetooth_mac = Column(String(512))

class MonitorReadings(Base):
    __tablename__ = 'monitor_readings'

    reading_id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    temp_c = Column(Integer)
    smoke = Column(Integer)
    humidity = Column(Integer)
    people = Column(Integer)

class DoorAccessLog(Base):
    __tablename__ = 'door_access_log'

    entry_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_accounts.id'), index=True)
    room = Column(Integer, ForeignKey('rooms.id'), index=True)
    timestamp = Column(DateTime)

class UserConnections(Base):
    __tablename__ = 'user_connection_history'

    entry_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_accounts.id'))
    timestamp = Column(DateTime)

class IotDoorConnections(Base):
    __tablename__ = 'door_connection_history'

    entry_id = Column(Integer, primary_key=True, index=True)
    door_id = Column(Integer, ForeignKey('iot_doors.id'))
    timestamp = Column(DateTime)

class IotMonitorConnections(Base):
    __tablename__ = 'monitor_connection_history'

    entry_id = Column(Integer, primary_key=True, index=True)
    monitor_id = Column(Integer, ForeignKey('iot_monitors.id'))
    timestamp = Column(DateTime)

# class IotEntity(Base):
#     __tablename__ = "iot_entities"

#     id = Column(Integer, primary_key=True, index=True)
#     bluetooth_mac = Column(String(512))
#     description = Column(String(512))
#     open_request = Column(Boolean, default=False)
#     time_seconds = Column(Integer, default=10)
#     authorized_users = relationship("User", secondary= 'user_iot_link')

# class UserAuthToIoTDev(Base):
#     __tablename__ = "user_iot_link"

#     user_id = Column(Integer, ForeignKey('user_accounts.id'), primary_key=True, index=True)
#     iot_entity_id = Column(Integer, ForeignKey('iot_entities.id'), primary_key=True, index=True)

# class DoorAccessLog(Base):
#     __tablename__ = "door_access_log"

#     entry_id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('user_accounts.id'))
#     iot_dev_bluetooth_mac = Column(Integer, ForeignKey('iot_entities.id'))
#     timestamp = Column(DateTime)

# class RoomSensorData(Base):
#     __tablename__ = "room_sensor_data"

#     # Data is now not related to a room. We should have a construct for rooms
#     reading_id = Column(Integer, primary_key=True, index=True)
#     humidity = Column(Integer)
#     people = Column(Integer)
#     temperature = Column(Integer)
#     smoke_sensor_reading = Column(Integer)
#     timestamp = Column(DateTime)

# TODO: Add table to store active sessions. May periodically clear.