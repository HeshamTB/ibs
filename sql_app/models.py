from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    passwd_salt = Column(String)
    is_active = Column(Boolean, default=True)

    authorized_devices = relationship("IotEntity", secondary= 'user_iot_link')


class IotEntity(Base):
    __tablename__ = "iot_entities"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("user_accounts.id"))

    authorized_users = relationship("User", secondary= 'user_iot_link')

class UserAuthToIoTDev(Base):
    __tablename__ = "user_iot_link"

    user_id = Column(Integer, ForeignKey('user_accounts.id'), primary_key=True, index=True)
    iot_entity_id = Column(Integer, ForeignKey('iot_entities.id'), primary_key=True, index=True)
