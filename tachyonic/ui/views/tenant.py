import logging

from tachyonic import app
from tachyonic import router
from tachyonic import jinja
from tachyonic.neutrino import constants as const
from tachyonic.neutrino.web.dom import Dom
from tachyonic.neutrino import Client

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
            if 'id' in response:
                dom = Dom()
                script = dom.create_element('script')
                name = response['name']
                js = "document.getElementById('open_tenant')"
                js += ".value = '%s';" % name
                js += "tenant_selected = true;"
                script.append(js)

            form = TenantModel(response, validate=False,
                               readonly=True, cols=2)
            tenant = dom.create_element('form')
            tenant.set_attribute('onsubmit', 'onsubmit="return false;"')
            tenant.append(form)
            if req.is_ajax():
                return dom.get()
            else:
                t = jinja.get_template('tachyonic.ui/ajax_wrapper.html')
                return t.render(title="View Account", content=dom.get())
        else:
            resp.redirect('/')
