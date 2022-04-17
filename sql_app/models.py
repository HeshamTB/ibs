from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
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

    authorized_devices = relationship("IotEntity", secondary= 'user_iot_link')


class IotEntity(Base):
    __tablename__ = "iot_entities"

    id = Column(Integer, primary_key=True, index=True)
    bluetooth_mac = Column(String(512))
    description = Column(String(512))
    open_request = Column(Boolean, default=False)
    authorized_users = relationship("User", secondary= 'user_iot_link')

class UserAuthToIoTDev(Base):
    __tablename__ = "user_iot_link"

    user_id = Column(Integer, ForeignKey('user_accounts.id'), primary_key=True, index=True)
    iot_entity_id = Column(Integer, ForeignKey('iot_entities.id'), primary_key=True, index=True)
