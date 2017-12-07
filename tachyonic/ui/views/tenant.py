import logging

from tachyonic import app
from tachyonic import router
from tachyonic import jinja
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import Client

from tachyonic.ui import menu

log = logging.getLogger(__name__)

menu.accounts.add('/View Account', '/tenant', 'tachyonic:login')


@app.resources()
class Tenant(object):
    """ class Tenant

    Adds and process requests to /tenant and /open_tenant routes.

    /tenant is used by the "View Account" Item in the accounts menu.
    /open_tenant is used by the "Open" button in the tenant search results.

    """

    def __init__(self):
        # VIEW TENANT
        router.add(const.HTTP_GET,
                   '/tenant',
                   self.view,
                   'tachyonic:login')
        router.add(const.HTTP_POST,
                   '/tenant',
                   self.view,
                   'tachyonic:login')
        # OPEN TENANT
        router.add(const.HTTP_GET,
                   '/open_tenant',
                   self.view,
                   'tachyonic:public')
        router.add(const.HTTP_POST,
                   '/open_tenant',
                   self.view,
                   'tachyonic:public')

    def view(self, req, resp):
        """Method view(req, resp)

        Used to process requests to /tenant and /open_tenant routes in order
        to display the tenant information.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
        """
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
