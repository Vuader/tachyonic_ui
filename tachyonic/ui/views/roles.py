from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import json
from collections import OrderedDict

from tachyonic import app
from tachyonic import router
from tachyonic.common import constants as const
from tachyonic.common import exceptions
from tachyonic.client import Client

from tachyonic.ui.views import ui
from tachyonic.ui.views.datatable import datatable
from tachyonic.ui import menu
from tachyonic.api.models.roles import Role as RoleModel

log = logging.getLogger(__name__)

menu.admin.add('/Accounts/Roles','/roles','roles:view')

@app.resources()
class Roles(object):
    def __init__(self):
        # VIEW ROLES
        router.add(const.HTTP_GET,
                   '/roles',
                   self.view,
                   'tachyonic:login')
        router.add(const.HTTP_GET,
                   '/roles/view/{role_id}',
                   self.view,
                   'roles:view')
        # ADD NEW ROLES
        router.add(const.HTTP_GET,
                   '/roles/create',
                   self.create,
                   'roles:admin')
        router.add(const.HTTP_POST,
                   '/roles/create',
                   self.create,
                   'roles:admin')
        # EDIT ROLES
        router.add(const.HTTP_GET,
                   '/roles/edit/{role_id}', self.edit,
                   'roles:admin')
        router.add(const.HTTP_POST,
                   '/roles/edit/{role_id}', self.edit,
                   'roles:admin')
        # DELETE ROLES
        router.add(const.HTTP_GET,
                   '/roles/delete/{role_id}', self.delete,
                   'roles:admin')

    def view(self, req, resp, role_id=None):
        if role_id is None:
            return_format = req.headers.get('X-Format')
            if return_format == "select2":
                api = Client(req.context['restapi'])
                headers, response = api.execute(
                    const.HTTP_GET, "/v1/roles/")
                result = []
                for r in response:
                    result.append({'id': r['id'], 'text': r['name']})
                return json.dumps(result, indent=4)
            else:
                fields = OrderedDict()
                fields['name'] = 'Role'
                fields['description'] = 'Description'
                dt = datatable(req, 'roles', '/v1/roles',
                fields, view_button=True, service=False)
                ui.view(req, resp, content=dt, title='Roles')
        else:
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/v1/role/%s" % (role_id,))
            form = RoleModel(response, validate=False, readonly=True)
            ui.view(req, resp, content=form, id=role_id, title='View Role',
                    view_form=True)

    def edit(self, req, resp, role_id=None):
        save = req.post.get('save', False)
        if req.method == const.HTTP_POST and save is not False:
            form = RoleModel(req.post, validate=True, readonly=True)
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_PUT, "/v1/role/%s" %
                                            (role_id,), form)
        else:
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/v1/role/%s" % (role_id,))
            form = RoleModel(response, validate=False)
            ui.edit(req, resp, content=form, id=role_id, title='Edit Role')

    def create(self, req, resp):
        if req.method == const.HTTP_POST:
            try:
                form = RoleModel(req.post, validate=True)
                api = Client(req.context['restapi'])
                headers, response = api.execute(const.HTTP_POST, "/v1/role", form)
                if 'id' in response:
                    id = response['id']
                    self.view(req, resp, role_id=id)
            except exceptions.HTTPBadRequest as e:
                form = RoleModel(req.post, validate=False)
                ui.create(req, resp, content=form, title='Create Role', error=[e])
        else:
            form = RoleModel(req.post, validate=False)
            ui.create(req, resp, content=form, title='Create Role')

    def delete(self, req, resp, role_id=None):
        api = Client(req.context['restapi'])
        headers, response = api.execute(const.HTTP_DELETE, "/v1/role/%s" % (role_id,))
        self.view(req, resp)
