# -*- coding: utf-8 -*-

import re
import falcon

from sqlalchemy.orm.exc import NoResultFound
from cerberus import Validator
from cerberus.errors import ValidationError

from app import log
from app.api.common import BaseResource
from app.utils.hooks import auth_required, authorised_user, admin_user
from app.utils.auth import encrypt_token, hash_password, verify_password, uuid
from app.model import User, UserInfo
from app.errors import (
    AppError,
    InvalidParameterError,
    UserNotExistsError,
    PasswordNotMatch,
)

LOG = log.get_logger()


FIELDS = {
    "username": {"type": "string", "required": True, "minlength": 4, "maxlength": 20},
    "email": {
        "type": "string",
        "regex": "[a-zA-Z0-9._-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,4}",
        "required": True,
        "maxlength": 320,
    },
    "password": {
        "type": "string",
        "regex": "[0-9a-zA-Z]\w{3,14}",
        "required": True,
        "minlength": 8,
        "maxlength": 64,
    },
    "info": {"type": "dict", "required": False},
    "shared_id": {"type": "string", "required": True},
}


def validate_user_create(req, res, resource, params):
    schema = {
        "username": FIELDS["username"],
        "email": FIELDS["email"],
        "password": FIELDS["password"]
    }

    v = Validator(schema)
    if not v.validate(req.context["data"]):
        raise InvalidParameterError(v.errors)


class Collection(BaseResource):
    """
    Handle for endpoint: /v1/users
    """

    @falcon.before(validate_user_create)
    def on_post(self, req, res):
        session = req.context["session"]
        user_req = req.context["data"]
        if user_req:
            user = User()
            user.username = user_req["username"]
            user.email = user_req["email"]
            user.password = hash_password(user_req["password"]).decode("utf-8")
            sid = uuid()
            user.sid = sid
            user.token = encrypt_token(sid).decode("utf-8")
            session.add(user)
            self.on_success(res, None)
        else:
            raise InvalidParameterError(req.context["data"])

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context["session"]
        user_dbs = session.query(User).all()
        if user_dbs:
            obj = [user.to_dict() for user in user_dbs]
            self.on_success(res, obj)
        else:
            raise AppError()

    @falcon.before(auth_required)
    def on_put(self, req, res):
        pass


class Item(BaseResource):
    """
    Handle for endpoint: /v1/users/{user_id}
    """

    @falcon.before(auth_required)
    def on_get(self, req, res, user_id):
        session = req.context["session"]
        try:
            user_db = User.find_one(session, user_id)
            self.on_success(res, user_db.to_dict())
        except NoResultFound:
            raise UserNotExistsError("user id: %s" % user_id)


class Self(BaseResource):
    """
    Handle for endpoint: /v1/users/self
    """

    LOGIN = "login"
    RESETPW = "resetpw"

    def on_get(self, req, res):
        cmd = re.split("\\W+", req.path)[-1:][0]
        if cmd == Self.LOGIN:
            self.process_login(req, res)
        elif cmd == Self.RESETPW:
            self.process_resetpw(req, res)

    def process_login(self, req, res):
        data = req.context["data"]
        email = data["email"]
        password = data["password"]
        session = req.context["session"]
        try:
            user_db = User.find_by_email(session, email)
            if verify_password(password, user_db.password.encode("utf-8")):
                self.on_success(res, user_db.to_dict())
            else:
                raise PasswordNotMatch()
        except NoResultFound:
            raise UserNotExistsError("User email: %s" % email)

    @falcon.before(auth_required)
    def process_resetpw(self, req, res):
        pass


class UserInformation(BaseResource):
    """
    Handle for endpoint: /v1/users/info/self
    """

    @falcon.before(authorised_user)
    def on_post(self, req, res):
        session = req.context["session"]
        user_req = req.context["data"]

        if user_req:
            userinfo_db = UserInfo.find_by_user_id(session=session, user_id=user_req["user_id"])
            userinfo = userinfo_db if userinfo_db else UserInfo()
            userinfo.user_id = user_req["user_id"]
            userinfo.address = user_req["address"]
            userinfo.dob = user_req["dob"]
            userinfo.contact = user_req["contact"]
            userinfo.nationality = user_req["nationality"]
            userinfo.profile_strength = user_req["profile_strength"]
            session.add(userinfo)
            self.on_success(res, None)
        else:
            raise InvalidParameterError(req.context["data"])


    @falcon.before(authorised_user)
    def on_get(self, req, res):
        session = req.context["session"]
        user_req = req.context["data"]

        try:
            userinfo_db = UserInfo.find_by_user_id(session=session, user_id=user_req["user_id"])
            self.on_success(res, userinfo_db.to_dict())
        except NoResultFound:
            raise UserNotExistsError("user id: %s" % user_req["user_id"])


class AllUserInformation(BaseResource):
    """
    Handle for endpoint: /v1/users/info
    """

    @falcon.before(admin_user)
    def on_post(self, req, res):
        session = req.context["session"]
        user_req = req.context["data"]

        if user_req:
            userinfo_db = UserInfo.find_by_user_id(session=session, user_id=user_req["user_id"])
            if userinfo_db:
                userinfo = userinfo_db
            else:
                raise UserNotExistsError("user id: %s" % user_req["user_id"])
            userinfo.user_id = user_req["user_id"]
            userinfo.address = user_req.get("address") if user_req.get("address") else userinfo.address
            userinfo.dob = user_req.get("dob") if user_req.get("dob") else userinfo.dob
            userinfo.contact = user_req.get("contact") if user_req.get("contact") else userinfo.contact
            userinfo.nationality = user_req.get("nationality") if user_req.get("nationality") else userinfo.nationality
            userinfo.profile_strength = user_req.get("profile_strength") if user_req.get("profile_strength") else userinfo.profile_strength
            userinfo.verified = user_req.get("verified") if user_req.get("verified") is not None else userinfo.verified
            session.add(userinfo)
            self.on_success(res, None)
        else:
            raise InvalidParameterError(req.context["data"])

    @falcon.before(admin_user)
    def on_get(self, req, res):
        session = req.context["session"]
        user_req = req.context["data"]

        try:
            if user_req.get("user_id"):
                user_db = [User.find_by_user_id(session=session, user_id=user_req["user_id"])]
            elif user_req.get("shared_id"):
                user_db = [User.find_by_shared_id(session=session, id=user_req["shared_id"])]
            else:
                user_db = session.query(User).all()
            if user_db:
                userinfo_db = []
                # fetching both user and userinfo table
                for user in user_db:
                    user_details = user.to_dict()
                    user_details.update(user.userinfo[0].to_dict() if user.userinfo else {})
                    userinfo_db.append(user_details)

            self.on_success(res, userinfo_db)
        except NoResultFound:
            raise UserNotExistsError("user id: %s, shared id: %s" % (user_req.get("user_id"), user_req.get("shared_id")))



