import logging
import re

from tachyonic import app
from tachyonic import router
from tachyonic import jinja
from tachyonic.neutrino import exceptions as exceptions
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import Client
from tachyonic.neutrino.exceptions import ClientError

from tachyonic.ui.auth import clear_session
from tachyonic.ui.auth import authenticated
from tachyonic.ui.menu import render_menus

log = logging.getLogger(__name__)


def resource(req):
    """ Function resource.

    Detects the resource from the request.
    Eg from http://localhost/ui/users/create it will detect and return
    the resource as 'users'.

    Args:
        req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).

    Returns:
        uri (str): the detected resource.
    """
    res = req.get_full_path().replace(req.get_script(), '')
    uri = res.split('?')[0].strip('/')
    uri = re.sub('/(view|edit|create|delete).*', '', uri)
    return uri


def view_access(req, subview):
    """ Function view_access(req, subview)

    Validates whether the request is authorized to
    access the view.

    Args:
        req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
        subview (str): The rest of the URI following the resource, eg '/create'.

    Returns:
        bool whether policy allows access to the view.
    """
    res = resource(req)
    subview = subview.strip('/')
    res = "%s/%s" % (res, subview)
    r = router.find(req.method, res)
    if r is not None:
        obj, methods, obj_kwargs, r_route, name = r
        if req.policy.validate(name):
            return True
    return False


def view(req, resp, **kwargs):
    """ Function view(req, resp, **kwargs).

    Function to generate, and write to the response body, the default view
    of a resource or resources in the Tachyonic UI.

    Args:
        req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
        resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
        kwargs (object): List of keyword objects to be passed when rendering the template.

    """
    res = resource(req)
    resource_id = kwargs.get('id', None)
    if 'config' not in kwargs:
        kwargs['config'] = req.config.get('_empty_')
    if resource_id is None:
        if view_access(req, '/create'):
            kwargs['create_url'] = "%s/%s/create" % (req.get_app(), res)
        t = jinja.get_template('tachyonic.ui/view.html')
    else:
        if view_access(req, "/edit/%s" % (resource_id,)):
            kwargs['edit_url'] = "%s/%s/edit/%s" % (req.get_app(), res, resource_id)
        kwargs['back_url'] = "%s/%s" % (req.get_app(), res)
        t = jinja.get_template('tachyonic.ui/view.html')

    resp.body = t.render(**kwargs)


def edit(req, resp, **kwargs):
    """ Function edit(req, resp, **kwargs).

    Function to generate, and write to the response body, the default edit
    view of a resource in the Tachyonic UI.

    Args:
        req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
        resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
        kwargs (object): List of keyword objects to be passed when rendering the template.

    """
    res = resource(req)
    resource_id = kwargs.get('id', None)
    if 'config' not in kwargs:
        kwargs['config'] = req.config.get('_empty_')
    if 'confirm' not in kwargs:
        kwargs['confirm'] = "Continue deleting item?"
    kwargs['save_url'] = "%s/%s/edit/%s" % (req.get_app(), res, resource_id)
    kwargs['cancel_url'] = "%s/%s/view/%s" % (req.get_app(), res, resource_id)
    kwargs['delete_url'] = "%s/%s/delete/%s" % (req.get_app(), res, resource_id)
    t = jinja.get_template('tachyonic.ui/view.html')
    resp.body = t.render(**kwargs)


def create(req, resp, **kwargs):
    """ Function create(req, resp, **kwargs).

    Function to generate, and write to the response body, the default view to
    create a resource in the Tachyonic UI.

    Args:
        req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
        resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
        kwargs (object): List of keyword objects to be passed when rendering the template.

    """
    res = resource(req)
    if 'config' not in kwargs:
        kwargs['config'] = req.config.get('_empty_')
    kwargs['created_url'] = "%s/%s/create" % (req.get_app(), res)
    kwargs['back_url'] = "%s/%s" % (req.get_app(), res)
    t = jinja.get_template('tachyonic.ui/view.html')
    resp.body = t.render(**kwargs)


@app.resources()
class Tachyonic(object):
    """ class Tachyon

    Adds and process requests to the following main routes of the Tachyonic UI:

    /
    /login
    /logout
    /expired
    """

    def __init__(self):
        # ADDING THE MAIN ROUTES
        router.add(const.HTTP_GET, '/', self.home, 'tachyonic:public')
        router.add(const.HTTP_POST, '/', self.home, 'tachyonic:public')
        router.add(const.HTTP_GET, '/login', self.login, 'tachyonic:public')
        router.add(const.HTTP_POST, '/login', self.login, 'tachyonic:public')
        router.add(const.HTTP_GET, '/logout', self.logout, 'tachyonic:public')
        router.add(const.HTTP_GET, '/expired', self.expired, 'tachyonic:public')

    def logout(self, req, resp):
        """ Method logout(req, resp)

        Used to process requests to the /logout route in order to log a user out.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).

        """
        clear_session(req)
        render_menus(req)
        router.view('/login', const.HTTP_POST, req, resp)

    def expired(self, req):
        """ Method logout(req)

        Used to process requests to the /expired route in order to log a user out
        after some time of inactivity. This is for example used by the messaging view
        to redirect to /expired.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).

        """
        clear_session(req)
        render_menus(req)
        raise exceptions.HTTPBadRequest(title="Authentication", description="Token Expired")

    def home(self, req, resp):
        """ Method home(req)

        Used to process requests to the root of the app (/).

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).

        """
        if req.session.get('token') is not None:
            tenant_name = ''
            tenant_selected = False
            if ('tenant_id' in req.context and
                        req.context['tenant_id'] is not None):
                api = Client(req.context['restapi'])
                server_headers, response = api.execute(const.HTTP_GET,
                                                       '/v1/tenant')
                if 'id' in response:
                    tenant_name = response['name']
                    tenant_selected = True

            t = jinja.get_template('tachyonic.ui/dashboard.html')
            resp.body = t.render(tenant_selected=tenant_selected, open_tenant=tenant_name)

        else:
            router.view('/login', const.HTTP_POST, req, resp)

    def login(self, req, resp):
        """ Method login(req, resp)

        Used to process requests to the /login route in order to log a user in.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).

        """
        username = req.post.get('username', '')
        password = req.post.get('password', '')
        domain = req.post.get('domain', 'default')
        error = []
        if username != '':
            api = Client(req.context['restapi'])
            try:
                auth = api.authenticate(username, password, domain)
                token = auth['token']
                req.session['token'] = token
                req.session['domain'] = domain
                authenticated(req, auth)
                jinja.request['DOMAINS'] = req.context['domains']
                render_menus(req)
            except ClientError as e:
                if e.status == const.HTTP_500:
                    clear_session(req)
                    error.append("RESTAPI Server Internal Error")
                else:
                    clear_session(req)
                    msg = "%s - %s" % (e.title, e.description)
                    error.append(msg)

        if req.session.get('token') is not None:
            resp.redirect('/')
        else:
            t = jinja.get_template('tachyonic.ui/login.html')
            resp.body = t.render(username=username,
                                 password=password,
                                 domain=domain,
                                 error=error)
