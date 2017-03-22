from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino.web.dom import Dom
from tachyonic.client import Client

from tachyonic.ui.models.tenants import Tenant as TenantModel
from tachyonic.ui import menu

log = logging.getLogger(__name__)

menu.accounts.add('/View Account','/tenant','tachyonic:login')

@app.resources()
class Tenant(object):
    def __init__(self):
        # VIEW USERS
        router.add(const.HTTP_GET,
                   '/tenant',
                   self.view,
                   'tachyonic:login')
        router.add(const.HTTP_POST,
                   '/tenant',
                   self.view,
                   'tachyonic:login')

    def view(self, req, resp):
        api = Client(req.context['restapi'])
        server_headers, response = api.execute(const.HTTP_GET, '/v1/tenant')
        if 'id' in response:
            dom = Dom()
            script = dom.create_element('script')
            name = response['name']
            js = "document.getElementById('open_tenant')"
            js += ".value = '%s'" % name
            script.append(js)

        form = TenantModel(response, validate=False,
                           readonly=True, cols=2)
        tenant = dom.create_element('form')
        tenant.set_attribute('onsubmit', 'onsubmit="return false;"')
        tenant.append(form)
        return dom.get()
