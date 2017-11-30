import logging
import json
from collections import OrderedDict

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import exceptions
from tachyonic.neutrino import Client
from tachyonic.api.models.roles import Role as RoleModel

from tachyonic.ui.views import ui
from tachyonic.ui.views.datatable import datatable
from tachyonic.ui import menu

log = logging.getLogger(__name__)

menu.admin.add('/Accounts/Roles', '/roles', 'roles:view')


@app.resources()
class Roles(object):
    """
    class Roles

    Adds and process requests to /roles... routes.

    Roles are used to control a user's access to URI's and menu items. Each route/menu item can
    be protected by a policy (eg. roles:view). These polices are tied to rules in the policies.json
    file (eg. ""roles:view": "Rule:is_root or Rule:is_ops". Also in this file is the mapping of
    rules to Roles (eg. "is_ops": "$context.roles:Operations" where Operations is the name of a defined Role)
    """

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
        """Method view(req, resp, role_id=None)

        Used to process requests to /roles and /roles/view/{role_id} in order
        to view roles or a particular role.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            role_id (str): UUID of a particular role to be viewed.
        """
        if role_id is None:
            return_format = req.headers.get('X-Format')
            if return_format == "select2":
                api = Client(req.context['restapi'])
                headers, response = api.execute(
                    const.HTTP_GET, "/v1/roles")
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
        """Method edit(req, resp, role_id=None)

        Used to process requests to /roles/edit/{role_id} in order to modify roles.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            role_id (str): UUID of the particular role to be modifed.
        """
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
        """Method create(req, resp)

        Used to process requests to /roles/create in order to create new roles.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
        """
        if req.method == const.HTTP_POST:
            try:
                form = RoleModel(req.post, validate=True)
                api = Client(req.context['restapi'])
                headers, response = api.execute(const.HTTP_POST, "/v1/role", form)
                if 'id' in response:
                    role_id = response['id']
                    self.view(req, resp, role_id=role_id)
            except exceptions.HTTPBadRequest as e:
                form = RoleModel(req.post, validate=False)
                ui.create(req, resp, content=form, title='Create Role', error=[e])
        else:
            form = RoleModel(req.post, validate=False)
            ui.create(req, resp, content=form, title='Create Role')

    def delete(self, req, resp, role_id=None):
        """Method delete(req, resp, role_id=None)

        Used to process requests to /roles/delete/{role_id} in order to delete roles.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            role_id (str): UUID of the particular role to be deleted.
        """
        api = Client(req.context['restapi'])
        headers, response = api.execute(const.HTTP_DELETE, "/v1/role/%s" % (role_id,))
        self.view(req, resp)
