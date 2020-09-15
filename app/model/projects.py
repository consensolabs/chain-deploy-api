# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey
from sqlalchemy import String, Integer, LargeBinary, Boolean, Date, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from app.model import Base, User


class Projects(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    name = Column(String(100), nullable=False)
    p_revenue = Column(Float,  nullable=True)
    p_net_income = Column(Float,  nullable=True)
    p_total_assets = Column(Float,  nullable=True)
    fund_source = Column(String(200), nullable=False)

    user = relationship("User", back_populates="projects")


    @classmethod
    def get_id(cls):
        return Projects.id

    @classmethod
    def find_by_user_id(cls, session, user_id):
        try:
            return session.query(Projects).filter(Projects.user_id == user_id)
        except NoResultFound:
            return None

    @classmethod
    def find_by_project_id(cls, session, project_id):
        try:
            return session.query(Projects).filter(Projects.id == project_id).one()
        except NoResultFound:
            return None

    FIELDS = {"name": str, "p_revenue": float,"p_net_income": float,
              "p_total_assets": float, "fund_source": str}

    FIELDS.update(Base.FIELDS)
    FIELDS.update(User.FIELDS)
