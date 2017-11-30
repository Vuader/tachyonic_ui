import logging
from collections import OrderedDict

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import exceptions
from tachyonic.neutrino import Client

from tachyonic.ui.views import ui
from tachyonic.ui.views.datatable import datatable
from tachyonic.ui import menu
from tachyonic.api.models.domains import Domain as DomainModel

log = logging.getLogger(__name__)

menu.admin.add('/Accounts/Domains', '/domains', 'domains:view')


@app.resources()
class Domains(object):
    """
    class Domains

    Adds and process requests to /domains... routes.

    Domains are used to logically separate resources in Tachyonic. For example,
    If a user is created within a domain, that user can not access resources that has
    been created within a different domain.
    """
    def __init__(self):
        # VIEW DOMAINS
        router.add(const.HTTP_GET,
                   '/domains',
                   self.view,
                   'domains:view')
        router.add(const.HTTP_GET,
                   '/domains/view/{domain_id}',
                   self.view,
                   'domains:view')
        # ADD NEW DOMAINS
        router.add(const.HTTP_GET,
                   '/domains/create',
                   self.create,
                   'domains:admin')
        router.add(const.HTTP_POST,
                   '/domains/create',
                   self.create,
                   'domains:admin')
        # EDIT DOMAINS
        router.add(const.HTTP_GET,
                   '/domains/edit/{domain_id}', self.edit,
                   'domains:admin')
        router.add(const.HTTP_POST,
                   '/domains/edit/{domain_id}', self.edit,
                   'domains:admin')
        # DELETE DOMAINS
        router.add(const.HTTP_GET,
                   '/domains/delete/{domain_id}', self.delete,
                   'domains:admin')

    def view(self, req, resp, domain_id=None):
        """Method view(req, resp, domain_id=None)

        Used to process requests to /domains and /domains/view/{domain_id} in order
        to view domains or a particular domain.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            domain_id (str): UUID of a particular domain to be viewed.
        """
        if domain_id is None:
            fields = OrderedDict()
            fields['name'] = 'Domain'
            dt = datatable(req, 'domains', '/v1/domains',
                           fields, view_button=True, service=False)
            ui.view(req, resp, content=dt, title='Domains')
        else:
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET,
                                            "/v1/domain/%s" % (domain_id,))
            form = DomainModel(response, validate=False, readonly=True)
            ui.view(req, resp, content=form, id=domain_id, title='View Domain',
                    view_form=True)

    def edit(self, req, resp, domain_id=None):
        """Method edit(req, resp, domain_id=None)

        Used to process requests to /domains/edit/{domain_id} in order to modify domains.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            domain_id (str): UUID of the particular domain to be modifed.
        """
        if req.method == const.HTTP_POST:
            form = DomainModel(req.post, validate=True, readonly=True)
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_PUT, "/v1/domain/%s" %
                                            (domain_id,), form)
        else:
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/v1/domain/%s" %
                                            (domain_id,))
            form = DomainModel(response, validate=False)
            ui.edit(req, resp, content=form, id=domain_id, title='Edit Domain')

    def create(self, req, resp):
        """Method create(req, resp)

        Used to process requests to /domains/create in order to create new Domains.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
        """
        if req.method == const.HTTP_POST:
            try:
                form = DomainModel(req.post, validate=True)
                api = Client(req.context['restapi'])
                headers, response = api.execute(const.HTTP_POST, "/v1/domain", form)
                if 'id' in response:
                    domain_id = response['id']
                    self.view(req, resp, domain_id=domain_id)
            except exceptions.HTTPBadRequest as e:
                form = DomainModel(req.post, validate=False)
                ui.create(req, resp, content=form, title='Create Domain', error=[e])
        else:
            form = DomainModel(req.post, validate=False)
            ui.create(req, resp, content=form, title='Create Domain')

    def delete(self, req, resp, domain_id=None):
        """Method delete(req, resp, domain_id=None)

        Used to process requests to /domains/delete/{domain_id} in order to delete domains.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            domain_id (str): UUID of the particular domain to be deleted.
        """
        api = Client(req.context['restapi'])
        headers, response = api.execute(const.HTTP_DELETE, "/v1/domain/%s" %
                                        (domain_id,))
        self.view(req, resp)
