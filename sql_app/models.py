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
    last_token = Column(String, nullable=True)
    connections = relationship("UserConnectionHistory")
    authorized_devices = relationship("IotEntity", secondary="user_iot_link", back_populates="authorized_users")
    connections = relationship("UserConnectionHistory")
    access_log = relationship("DoorAccessLog", back_populates="user")

class IotEntity(Base):
    __tablename__ = "iot_entities"

    id = Column(Integer, primary_key=True, index=True)
    bluetooth_mac = Column(String(512), index=True, unique=True)
    description = Column(String(512))
    open_request = Column(Boolean, default=False)
    time_seconds = Column(Integer, default=10)
    acces_list_counter = Column(Integer, default=0)
    force_close = Column(Boolean, default=False)
    state = Column(Boolean, default=False) # True is open, False is closed
    authorized_users = relationship("User", secondary="user_iot_link", back_populates="authorized_devices")
    access_log = relationship("DoorAccessLog", back_populates="iot_device") # one-to-many
    monitor = relationship("Monitors", back_populates="door", uselist=False) # one-to-one

class Monitors(Base):
    __tablename__ = "monitors"

    id = Column(Integer, primary_key=True)
    bluetooth_mac = Column(String(512), index=True, unique=True)
    description = Column(String(512))
    humidity = Column(Integer, default=0)
    people = Column(Integer, default=0)
    temperature = Column(Integer, default=0)
    smoke_sensor_reading = Column(Integer, default=0)
    door_id = Column(Integer, ForeignKey("iot_entities.id"))
    door = relationship("IotEntity", back_populates="monitor")
    sensor_history = relationship("RoomSensorData", back_populates="monitor")

class UserAuthToIoTDev(Base):
    __tablename__ = "user_iot_link"

    user_id = Column(Integer, ForeignKey("user_accounts.id"), primary_key=True)
    iot_id = Column(Integer, ForeignKey("iot_entities.id"), primary_key=True)
    timestamp = Column(DateTime)

class DoorAccessLog(Base):
    __tablename__ = "door_access_log"

    entry_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_accounts.id'), index=True)
    user = relationship("User", back_populates="access_log")
    iot_id = Column(Integer, ForeignKey('iot_entities.id'), index=True)
    iot_device = relationship("IotEntity", back_populates="access_log")
    command = Column(String(16))
    timestamp = Column(DateTime)

class RoomSensorData(Base):
    __tablename__ = "room_sensor_data"

    # Data is now not related to a room. We should have a construct for rooms
    reading_id = Column(Integer, primary_key=True, index=True)
    humidity = Column(Integer)
    people = Column(Integer)
    temperature = Column(Integer)
    smoke_sensor_reading = Column(Integer)
    timestamp = Column(DateTime)
    monitor_id = Column(Integer, ForeignKey("monitors.id"), index=True)
    monitor = relationship("Monitors", back_populates="sensor_history")

class UserConnectionHistory(Base):
    __tablename__ = "user_connection_history"

    reading_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), index=True)
    timestamp = Column(DateTime)
    # TODO: add ip

# TODO: Add table to store active sessions. May periodically clear.