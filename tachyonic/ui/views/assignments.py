import logging
from collections import OrderedDict

from tachyonic.neutrino import constants as const
from tachyonic.neutrino import exceptions
from tachyonic.neutrino.wsgi import jinja
from tachyonic.neutrino.wsgi import app
from tachyonic.neutrino.wsgi import router
from tachyonic.neutrino.client import Client

from tachyonic.ui.views import ui
from tachyonic.ui.views.datatable import datatable
from tachyonic.ui import menu
from tachyonic.ui.views.select import select
from tachyonic.api.models.users import User as UserModel

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

