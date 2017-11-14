import logging
from collections import OrderedDict

from tachyonic import app
from tachyonic import router
from tachyonic.common import constants as const
from tachyonic.common import exceptions
from tachyonic.client import Client

from tachyonic.ui.views import ui
from tachyonic.ui.views.datatable import datatable
from tachyonic.ui import menu
from tachyonic.api.models.tenants import Tenant as TenantModel

log = logging.getLogger(__name__)

menu.admin.add('/Accounts/Tenants','/tenants','tenants:view')

@app.resources()
class Tenant(object):
    def __init__(self):
        # VIEW TENANTS
        router.add(const.HTTP_GET,
                   '/tenants',
                   self.view,
                   'tenants:view')
        router.add(const.HTTP_GET,
                   '/tenants/view/{tenant_id}',
                   self.view,
                   'tenants:view')
        # ADD NEW TENANTS
        router.add(const.HTTP_GET,
                   '/tenants/create',
                   self.create,
                   'tenants:admin')
        router.add(const.HTTP_POST,
                   '/tenants/create',
                   self.create,
                   'tenants:admin')
        # EDIT TENANTS
        router.add(const.HTTP_GET,
                   '/tenants/edit/{tenant_id}', self.edit,
                   'tenants:admin')
        router.add(const.HTTP_POST,
                   '/tenants/edit/{tenant_id}', self.edit,
                   'tenants:admin')
        # DELETE TENANTS
        router.add(const.HTTP_GET,
                   '/tenants/delete/{tenant_id}', self.delete,
                   'tenants:admin')

    def view(self, req, resp, tenant_id=None):
        extra = "<script>tenant_form();</script>"
        if tenant_id is None:
            fields = OrderedDict()
            fields['name'] = 'Name'
            fields['tenant_type'] = 'Type'
            fields['creation_time'] = 'Created'
            fields['id'] = 'Unique ID'
            dt = datatable(req, 'tenant', '/v1/tenants',
                           fields, view_button=True, service=False)
            ui.view(req, resp, content=dt,
                    title='Tenants',config=app.config.get('tenants'))
        else:
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/v1/tenant/%s" %
                                            (tenant_id,))
            form = TenantModel(response, validate=False,
                                readonly=True, cols=2)
            ui.view(req, resp, content=form, id=tenant_id, title='View Tenant',
                    view_form=True, extra=extra,
                    config=app.config.get('tenants'))

    def edit(self, req, resp, tenant_id=None):
        extra = "<script>tenant_form();</script>"
        if req.method == const.HTTP_POST:
            form = TenantModel(req.post, validate=True, readonly=True, cols=2)
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_PUT, "/v1/tenant/%s" %
                                            (tenant_id,), form)
        else:
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/v1/tenant/%s" %
                                            (tenant_id,))
            form = TenantModel(response, validate=False, cols=2)
            ui.edit(req, resp, content=form, id=tenant_id, title='Edit Tenant',
                 extra=extra)

    def create(self, req, resp):
        extra = "<script>tenant_form();</script>"
        if req.method == const.HTTP_POST:
            try:
                form = TenantModel(req.post, validate=True, cols=2)
                api = Client(req.context['restapi'])
                headers, response = api.execute(const.HTTP_POST, "/v1/tenant", form)
                if 'id' in response:
                    id = response['id']
                    self.view(req, resp, tenant_id=id)
            except exceptions.HTTPBadRequest as e:
                form = TenantModel(req.post, validate=False, cols=2)
                ui.create(req, resp, content=form, title='Create Tenant',
                       error=[e], extra=extra)
        else:
            form = TenantModel(req.post, validate=False, cols=2)
            ui.create(req, resp, content=form, title='Create Tenant', extra=extra)

    def delete(self, req, resp, tenant_id=None):
        api = Client(req.context['restapi'])
        headers, response = api.execute(const.HTTP_DELETE, "/v1/tenant/%s" %
                                        (tenant_id,))
        self.view(req, resp)
