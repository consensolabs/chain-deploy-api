# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey
from sqlalchemy import String, Integer, LargeBinary, Boolean, Date, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from app.model import Base, User


class UserInfo(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    address = Column(String(150), nullable=False)
    dob = Column(Date, nullable=False)
    contact = Column(String(15), nullable=True)
    nationality = Column(String(20), nullable=False)
    verified = Column(Boolean, nullable=False, default=False)
    profile_strength = Column(Integer,  nullable=True)
    revenue = Column(Float,  nullable=True)
    net_income = Column(Float,  nullable=True)
    total_assets = Column(Float,  nullable=True)

    user = relationship("User", back_populates="userinfo")

    def __repr__(self):
        return "<UserInfo(adrress='%s', dob='%s')>" % (
            self.address,
            self.dob,
        )

    @classmethod
    def get_id(cls):
        return UserInfo.id

    @classmethod
    def find_by_user_id(cls, session, user_id):
        try:
            return session.query(UserInfo).filter(UserInfo.user_id == user_id).one()
        except NoResultFound:
            return None

    FIELDS = {"address": str, "dob": str, "contact": str, "nationality": str,
              "verified": bool, "profile_strength": int, "revenue": float,
              "net_income": float, "total_assets": float}

    FIELDS.update(Base.FIELDS)
    FIELDS.update(User.FIELDS)
