import logging
from collections import OrderedDict

from tachyonic import jinja
from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import exceptions
from tachyonic.neutrino import Client
from tachyonic.api.models.users import User as UserModel

from tachyonic.ui.views import ui
from tachyonic.ui.views.datatable import datatable
from tachyonic.ui import menu
from tachyonic.ui.views.select import select

log = logging.getLogger(__name__)

menu.admin.add('/Accounts/Users', '/users', 'users:view')


@app.resources()
class User(object):
    """
    class User

    Adds and process requests to /users... routes.

    In order to log in and make use of the Tachyonic Framework, users require
    accounts. This class is used create, update, and delete user accounts.
    """
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
        """Method view(req, resp, user_id=None)

        Used to process requests to /users and /users/view/{user_id} in order
        to view users or a particular user.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            user_id (str): UUID of a particular user to be viewed.
        """
        if user_id is None:
            fields = OrderedDict()
            fields['username'] = 'Username'
            fields['email'] = 'Email'
            fields['name'] = 'Fullname'
            fields['employer'] = 'Employer'
            dt = datatable(req, 'users', '/v1/users',
                           fields, view_button=True, service=False)
            ui.view(req, resp, content=dt, title='Users',
                    config=app.config.get('users'))
        else:
            api = Client(req.context['restapi'])
            headers, assignments = api.execute(const.HTTP_GET, "/v1/user/roles/%s" % (user_id,))
            headers, response = api.execute(const.HTTP_GET, "/v1/user/%s" % (user_id,))
            t = jinja.get_template('tachyonic.ui/assignments.html')
            extra = t.render(readonly=True,
                             assignments=assignments)
            form = UserModel(response, validate=False, readonly=True, cols=2)
            ui.view(req, resp, content=form, id=user_id, title='View User',
                    view_form=True, extra=extra, config=app.config.get('users'))

    def assign(self, req, resp):
        """ method assign(req, resp).

        Used by method edit() in order to assign a role to a user account.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
        """
        api = Client(req.context['restapi'])
        user_id = req.post.get('user_id')
        role = req.post.get('role')
        remove = req.post.get('remove')
        if role == '':
            role = None
        domain = req.post.get('assign_domain_id')
        if domain == '':
            domain = None
        tenant_id = req.post.get('assign_tenant_id')
        if tenant_id == '':
            tenant_id = None

        url = "/v1/user/role"
        url += "/%s" % user_id

        if role is not None and domain is not None:
            url += "/%s" % role
            url += "/%s" % domain
            if tenant_id is not None:
                url += "/%s" % tenant_id
            if remove == "True":
                headers, assignments = api.execute(const.HTTP_DELETE, url)
            else:
                headers, assignments = api.execute(const.HTTP_POST, url)

    def edit(self, req, resp, user_id=None):
        """Method edit(req, resp, user_id=None)

        Used to process requests to /users/edit/{user_id} in order to modify users.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            user_id (str): UUID of the particular user to be modifed.
        """
        save = req.post.get('save', False)
        if req.method == const.HTTP_POST and save is not False:
            form = UserModel(req.post, validate=True, readonly=True, cols=2)
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_PUT, "/v1/user/%s" %
                                            (user_id,), form)
        else:
            self.assign(req, resp)
            api_fields = OrderedDict()
            api_fields['id'] = None
            api_fields['name'] = "Name"
            api_fields['domain_id'] = None
            t = jinja.get_template('tachyonic.ui/select.js')
            select_js = t.render()
            change_js = select_js
            t = jinja.get_template('tachyonic.ui/select-else.js')
            select_js += t.render()
            tenants = select(req, 'tenant_assignment', '/v1/search',
                             api_fields,
                             select=select_js,
                             change=change_js,
                             placeholder="Tenant Name",
                             keywords_mode=False)
            api = Client(req.context['restapi'])
            headers, assignments = api.execute(const.HTTP_GET, "/v1/user/roles/%s" % (user_id,))
            headers, response = api.execute(const.HTTP_GET, "/v1/user/%s" % (user_id,))
            all_roles = []
            all_domains = []
            if req.context['is_root'] is True:
                headers, roles = api.execute(const.HTTP_GET, "/v1/roles")
                for a in roles:
                    all_roles.append(a)
                headers, domains = api.execute(const.HTTP_GET, "/v1/domains")
                for a in domains:
                    all_domains.append(a)

            form = UserModel(response, validate=False, cols=2)
            t = jinja.get_template('tachyonic.ui/assignments.html')
            extra = t.render(tenants=tenants,
                             assignments=assignments,
                             user_id=user_id,
                             all_domains=all_domains,
                             all_roles=all_roles)
            ui.edit(req, resp, content=form, id=user_id, title='Edit User',
                    extra=extra)

    def create(self, req, resp):
        """Method create(req, resp)

        Used to process requests to /users/create in order to create new users.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
        """
        if req.method == const.HTTP_POST:
            try:
                form = UserModel(req.post, validate=True, cols=2)
                api = Client(req.context['restapi'])
                headers, response = api.execute(const.HTTP_POST, "/v1/user", form)
                if 'id' in response:
                    user_id = response['id']
                    self.edit(req, resp, user_id=user_id)
            except exceptions.HTTPBadRequest as e:
                form = UserModel(req.post, validate=False, cols=2)
                ui.create(req, resp, content=form, title='Create User', error=[e])
        else:
            form = UserModel(req.post, validate=False, cols=2)
            ui.create(req, resp, content=form, title='Create User')

    def delete(self, req, resp, user_id=None):
        """Method delete(req, resp, user_id=None)

        Used to process requests to /users/delete/{user_id} in order to delete users.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            user_id (str): UUID of the particular user to be deleted.
        """
        api = Client(req.context['restapi'])
        headers, response = api.execute(const.HTTP_DELETE, "/v1/user/%s" % (user_id,))
        self.view(req, resp)
