from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    username = Column(String, default=None)
    group_url = Column(String, default=None)


class Groups(Base):
    __tablename__ = 'Groups'
    id = Column(Integer, primary_key=True)
    course = Column(Integer)
    group_name = Column(String, unique=True)
    group_url = Column(String)

