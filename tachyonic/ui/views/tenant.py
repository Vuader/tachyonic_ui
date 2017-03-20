from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino.web.dom import Dom
from tachyonic.client import Client

from tachyonic.ui.models.tenants import Tenant as TenantModel

log = logging.getLogger(__name__)


@app.resources()
class Tenant(object):
    def __init__(self):
        # VIEW USERS
        router.add(const.HTTP_GET,
                   '/tenant',
                   self.view,
                   'tachyonic:login')

    def view(self, req, resp):
        api = Client(req.context['restapi'])
        pass
