from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from collections import OrderedDict

from tachyonic import jinja
from tachyonic import app
from tachyonic import router
from tachyonic.common import constants as const
from tachyonic.common import exceptions
from tachyonic.client import Client

from tachyonic.ui.views import ui
from tachyonic.ui.views.datatable import datatable
from tachyonic.ui import menu
from tachyonic.api.models.users import User as UserModel
from tachyonic.ui.views.select import select

log = logging.getLogger(__name__)

@app.resources()
class Assignments(object):
    def __init__(self):
        router.add(const.HTTP_POST,
                   '/assignments',
                   self.assign,
                   'users:admin')

    def assign(self, req, resp):
        api = Client(req.context['restapi'])
        user_id = req.post.get('user_id')
        role = req.post.get('role')
        if role == '':
            role = None
        domain = req.post.get('domain')
        if domain == '':
            domain = None
        tenant_id = req.post.get('tenant_id')
        if tenant_id == '':
            tenant_id = None

        url = "/v1/user/role"
        url += "/%s" % user_id
        url += "/%s" % role
        url += "/%s" % domain

        if role is not None and domain is not None:
            if tenant_id is not None:
                url += "/%s" % tenant_id
            headers, assignments = api.execute(const.HTTP_POST, url)

        router.view("/users/edit/%s" % user_id, const.HTTP_GET, req, resp)

