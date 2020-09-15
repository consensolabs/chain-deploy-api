# -*- coding: utf-8 -*-

import falcon

from app import log
from app.utils.auth import decrypt_token
from app.errors import UnauthorizedError
from falcon.http_status import HTTPStatus


LOG = log.get_logger()


class AuthHandler(object):
    def process_request(self, req, res, resource=None):
        LOG.debug("Authorization: %s", req.auth)
        if req.auth is not None:
            token = decrypt_token(req.auth)
            if token is None:
                raise UnauthorizedError("Invalid auth token: %s" % req.auth)
            else:
                req.context["auth_user"] = token.decode("utf-8")
        else:
            req.context["auth_user"] = None



class HandleCORS(object):
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
        if req.method == 'OPTIONS':
            raise HTTPStatus(falcon.HTTP_200, body='\n')
