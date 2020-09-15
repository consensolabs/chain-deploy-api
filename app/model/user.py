# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import String, Integer, LargeBinary
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from app.model import Base
from app.config import UUID_LEN
from app.utils import alchemy


class User(Base):

    user_id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False)
    email = Column(String(320), unique=True, nullable=False)
    password = Column(String(80), nullable=False)
    token = Column(String(255), nullable=False)

    # intentionally assigned for user related service such as resetting password: kind of internal user secret key
    sid = Column(String(UUID_LEN), nullable=False)

    userinfo = relationship("UserInfo", back_populates="user")
    userroles = relationship("UserRoles", back_populates="user")
    projects = relationship("Projects", back_populates="user")

    def __repr__(self):
        return "<User(name='%s', email='%s', token='%s', info='%s')>" % (
            self.username,
            self.email,
            self.token,
            self.info,
        )

    @classmethod
    def get_id(cls):
        return User.user_id

    @classmethod
    def find_by_email(cls, session, email):
        return session.query(User).filter(User.email == email).one()

    @classmethod
    def find_by_sid(cls, session, sid):
        return session.query(User).filter(User.sid == sid).one()

    @classmethod
    def find_by_shared_id(cls, session, id):

        try:
            return session.query(User).filter(User.shared_id == id).one()
        except NoResultFound:
            return None

    @classmethod
    def find_by_user_id(cls, session, user_id):
        try:
            return session.query(User).filter(User.user_id == user_id).one()
        except NoResultFound:
            return None

    FIELDS = {"username": str, "email": str, "info": alchemy.passby, "token": str, "user_id": int}

    FIELDS.update(Base.FIELDS)
