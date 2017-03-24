from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from collections import OrderedDict

from tachyonic import jinja
from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import exceptions
from tachyonic.client import Client

from tachyonic.ui.views import ui
from tachyonic.ui.views.datatable import datatable
from tachyonic.ui import menu
from tachyonic.ui.models.users import User as UserModel
from tachyonic.ui.views.select import select

log = logging.getLogger(__name__)

menu.admin.add('/Accounts/Users','/users','users:view')


@app.resources()
class User(object):
    def __init__(self):
        # VIEW USERS
        router.add(const.HTTP_GET,
                   '/users',
                   self.view,
                   'users:view')
        router.add(const.HTTP_GET,
                   '/users/view/{user_id}',
                   self.view,
                   'users:view')
        # ADD NEW USERS
        router.add(const.HTTP_GET,
                   '/users/create',
                   self.create,
                   'users:admin')
        router.add(const.HTTP_POST,
                   '/users/create',
                   self.create,
                   'users:admin')
        # EDIT USERS
        router.add(const.HTTP_GET,
                   '/users/edit/{user_id}', self.edit,
                   'users:admin')
        router.add(const.HTTP_POST,
                   '/users/edit/{user_id}', self.edit,
                   'users:admin')
        # DELETE USERS
        router.add(const.HTTP_GET,
                   '/users/delete/{user_id}', self.delete,
                   'users:admin')

    def view(self, req, resp, user_id=None):
        if user_id is None:
            fields = OrderedDict()
            fields['username'] = 'Username'
            fields['email'] = 'Email'
            fields['name'] = 'Fullname'
            fields['employer'] = 'Employer'
            dt = datatable(req, 'users', '/v1/users',
                           fields, view_button=True, service=False)
            ui.view(req, resp, content=dt, title='Users')
        else:
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/v1/user/%s" % (user_id,))
            form = UserModel(response, validate=False, readonly=True, cols=2)
            ui.view(req, resp, content=form, id=user_id, title='View User',
                    view_form=True)

    def edit(self, req, resp, user_id=None):
        if req.method == const.HTTP_POST:
            form = UserModel(req.post, validate=True, readonly=True, cols=2)
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_PUT, "/v1/user/%s" %
                                            (user_id,), form)
        else:
            api_fields = OrderedDict()
            api_fields['id'] = "ID"
            api_fields['name'] = "Name"
            tenants = select(req, 'tenant_assignment', '/v1/search',
                      api_fields,
                      #select=select_js,
                      placeholder="Tenant Name",
                      keywords_mode=True)
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/v1/user/%s" % (user_id,))
            form = UserModel(response, validate=False, cols=2)
            t = jinja.get_template('tachyonic.ui/assignments.html')
            extra = t.render(tenants=tenants)
            ui.edit(req, resp, content=form, id=user_id, title='Edit User',
                    extra=extra)

    def create(self, req, resp):
        if req.method == const.HTTP_POST:
            try:
                form = UserModel(req.post, validate=True, cols=2)
                api = Client(req.context['restapi'])
                headers, response = api.execute(const.HTTP_POST, "/v1/user", form)
                if 'id' in response:
                    id = response['id']
                    self.view(req, resp, user_id=id)
            except exceptions.HTTPBadRequest as e:
                form = UserModel(req.post, validate=False, cols=2)
                ui.create(req, resp, content=form, title='Create User', error=[e])
        else:
            form = UserModel(req.post, validate=False, cols=2)
            ui.create(req, resp, content=form, title='Create User')

    def delete(self, req, resp, user_id=None):
        api = Client(req.context['restapi'])
        headers, response = api.execute(const.HTTP_DELETE, "/v1/user/%s" % (user_id,))
        self.view(req, resp)
