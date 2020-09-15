# -*- coding: utf-8 -*-

import re
import falcon

from sqlalchemy.orm.exc import NoResultFound
from cerberus import Validator
from cerberus.errors import ValidationError

from app import log
from app.api.common import BaseResource
from app.utils.hooks import auth_required, authorised_user
from app.utils.auth import encrypt_token, hash_password, verify_password, uuid
from app.model import User, UserInfo
from app.errors import (
    AppError,
    InvalidParameterError,
    UserNotExistsError,
    PasswordNotMatch,
)
from lib.deployment import create_node

LOG = log.get_logger()

class Deployment(BaseResource):
    """
    Handle for endpoint: /v1/deploy
    """

    # @falcon.before(validate_user_create)
    # def on_post(self, req, res):
    #     session = req.context["session"]
    #     user_req = req.context["data"]
    #     if user_req:
    #         user = User()
    #         user.username = user_req["username"]
    #         user.email = user_req["email"]
    #         user.password = hash_password(user_req["password"]).decode("utf-8")
    #         sid = uuid()
    #         user.sid = sid
    #         user.token = encrypt_token(sid).decode("utf-8")
    #         session.add(user)
    #         self.on_success(res, None)
    #     else:
    #         raise InvalidParameterError(req.context["data"])

    @falcon.before(auth_required)
    def on_get(self, req, res):
        user_req = req.context["data"]
        if user_req.get("task") == "ec2":
            create_node()
            obj = {}
            self.on_success(res, obj)
        else:
            raise AppError()

    @falcon.before(auth_required)
    def on_put(self, req, res):
        pass
