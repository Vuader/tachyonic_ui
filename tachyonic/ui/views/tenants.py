from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from collections import OrderedDict

from tachyonic import app
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import exceptions
from tachyonic.common.client import Client

from tachyonic.ui.views import ui
from tachyonic.ui.views.datatable import datatable
from tachyonic.ui import menu
from tachyonic.ui.models.tenants import Tenant as TenantModel

log = logging.getLogger(__name__)

menu.admin.add('/Accounts/Tenants','/tenants','tenants:view')

@app.resources()
class Tenant(object):
    def __init__(self, app):
        # VIEW TENANTS
        app.router.add(const.HTTP_GET,
                       '/tenants',
                       self.view,
                       'tenants:view')
        app.router.add(const.HTTP_GET,
                       '/tenants/view/{tenant_id}',
                       self.view,
                       'tenants:view')
        # ADD NEW TENANTS
        app.router.add(const.HTTP_GET,
                       '/tenants/create',
                       self.create,
                       'tenants:admin')
        app.router.add(const.HTTP_POST,
                       '/tenants/create',
                       self.create,
                       'tenants:admin')
        # EDIT TENANTS
        app.router.add(const.HTTP_GET,
                       '/tenants/edit/{tenant_id}', self.edit,
                       'tenants:admin')
        app.router.add(const.HTTP_POST,
                       '/tenants/edit/{tenant_id}', self.edit,
                       'tenants:admin')
        # DELETE TENANTS
        app.router.add(const.HTTP_GET,
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
            dt = datatable(req, 'tenant', '/tenants',
                           fields, view_button=True, service=False)
            ui.view(req, resp, content=dt, title='Tenants')
        else:
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/tenants/%s" %
                                            (tenant_id,))
            form = TenantModel(response, validate=False,
                                readonly=True, cols=2)
            ui.view(req, resp, content=form, id=tenant_id, title='View Tenant',
                    view_form=True, extra=extra)

    def edit(self, req, resp, tenant_id=None):
        extra = "<script>tenant_form();</script>"
        if req.method == const.HTTP_POST:
            form = TenantModel(req.post, validate=True, readonly=True, cols=2)
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_PUT, "/tenants/%s" %
                                            (tenant_id,), form)
        else:
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/tenants/%s" %
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
                headers, response = api.execute(const.HTTP_POST, "/tenants", form)
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
        headers, response = api.execute(const.HTTP_DELETE, "/tenants/%s" %
                                        (tenant_id,))
        self.view(req, resp)
