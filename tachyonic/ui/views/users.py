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
from tachyonic.ui.models.users import User as UserModel

log = logging.getLogger(__name__)

menu.admin.add('/Accounts/Users','/users','users:view')

@app.resources()
class User(object):
    def __init__(self, app):
        # VIEW USERS
        app.router.add(const.HTTP_GET,
                       '/users',
                       self.view,
                       'users:view')
        app.router.add(const.HTTP_GET,
                       '/users/view/{user_id}',
                       self.view,
                       'users:view')
        # ADD NEW USERS
        app.router.add(const.HTTP_GET,
                       '/users/create',
                       self.create,
                       'users:admin')
        app.router.add(const.HTTP_POST,
                       '/users/create',
                       self.create,
                       'users:admin')
        # EDIT USERS
        app.router.add(const.HTTP_GET,
                       '/users/edit/{user_id}', self.edit,
                       'users:admin')
        app.router.add(const.HTTP_POST,
                       '/users/edit/{user_id}', self.edit,
                       'users:admin')
        # DELETE USERS
        app.router.add(const.HTTP_GET,
                       '/users/delete/{user_id}', self.delete,
                       'users:admin')

    def view(self, req, resp, user_id=None):
        if user_id is None:
            fields = OrderedDict()
            fields['username'] = 'Username'
            fields['email'] = 'Email'
            fields['name'] = 'Fullname'
            fields['employer'] = 'Employer'
            dt = datatable(req, 'users', '/users',
                           fields, view_button=True, service=False)
            ui.view(req, resp, content=dt, title='Users')
        else:
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/users/%s" % (user_id,))
            form = UserModel(response, validate=False, readonly=True, cols=2)
            ui.view(req, resp, content=form, id=user_id, title='View User',
                    view_form=True)

    def edit(self, req, resp, user_id=None):
        if req.method == const.HTTP_POST:
            form = UserModel(req.post, validate=True, readonly=True, cols=2)
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_PUT, "/users/%s" %
                                            (user_id,), form)
        else:
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/users/%s" % (user_id,))
            form = UserModel(response, validate=False, cols=2)
            ui.edit(req, resp, content=form, id=user_id, title='Edit User')

    def create(self, req, resp):
        if req.method == const.HTTP_POST:
            try:
                form = UserModel(req.post, validate=True, cols=2)
                api = Client(req.context['restapi'])
                headers, response = api.execute(const.HTTP_POST, "/users", form)
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
        headers, response = api.execute(const.HTTP_DELETE, "/users/%s" % (user_id,))
        self.view(req, resp)
