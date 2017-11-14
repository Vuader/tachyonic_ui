import logging

from tachyonic import app
from tachyonic import router
from tachyonic import jinja
from tachyonic.neutrino import constants as const
from tachyonic.neutrino.web.dom import Dom
from tachyonic.client import Client

from tachyonic.api.models.tenants import Tenant as TenantModel
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
        router.add(const.HTTP_GET,
                   '/open_tenant',
                   self.view,
                   'tachyonic:public')
        router.add(const.HTTP_POST,
                   '/open_tenant',
                   self.view,
                   'tachyonic:public')

    def view(self, req, resp):
        if req.context['login'] is True:
            api = Client(req.context['restapi'])
            server_headers, response = api.execute(const.HTTP_GET, '/v1/tenant')

            if req.is_ajax():
                t = jinja.get_template('tachyonic.ui/view_account.html')
                return t.render(title="Account", content=response)
            else:
                t = jinja.get_template('tachyonic.ui/ajax_wrapper.html')
                return t.render(title="Account", content=response)
        else:
            resp.redirect('/')
