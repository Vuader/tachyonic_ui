from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import re

from tachyonic import app
from tachyonic import router
from tachyonic import jinja
from tachyonic.common import exceptions as exceptions
from tachyonic.common import constants as const
from tachyonic.client import Client
from tachyonic.common.exceptions import ClientError
from tachyonic.neutrino.config import Config

from tachyonic.ui.auth import clear_session
from tachyonic.ui.auth import authenticated
from tachyonic.ui.menu import render_menus

log = logging.getLogger(__name__)

def resource(req):
    res = req.get_full_path().replace(req.get_script(),'')
    uri = res.split('?')[0].strip('/')
    uri = re.sub('/(view|edit|create|delete).*','',uri)
    return uri

def route(req, route):
    route = route.strip('/')
    return router._match(const.HTTP_GET, route)


def view_access(req, subview):
    res = resource(req)
    subview = subview.strip('/')
    res = "%s/%s" % (res, subview)
    r = route(req, res)
    if r is not None:
        r_route, obj_kwargs = r
        method, r_route, obj, name = r_route
        if req.policy.validate(name):
            return True
    return False


def view(req, resp, **kwargs):
    res = resource(req)
    id = kwargs.get('id', None)
    if 'config' not in kwargs:
        kwargs['config'] = req.config.get('_empty_')
    if id is None:
        if view_access(req, '/create'):
            kwargs['create_url'] = "%s/%s/create" % (req.get_app(), res)
        t = jinja.get_template('tachyonic.ui/view.html')
    else:
        if view_access(req, "/edit/%s" % (id,)):
            kwargs['edit_url'] = "%s/%s/edit/%s" % (req.get_app(), res, id)
        kwargs['back_url'] = "%s/%s" % (req.get_app(),res)
        t = jinja.get_template('tachyonic.ui/view.html')

    resp.body = t.render(**kwargs)


def edit(req, resp, **kwargs):
    res = resource(req)
    id = kwargs.get('id', None)
    if 'config' not in kwargs:
        kwargs['config'] = req.config.get('_empty_')
    if 'confirm' not in kwargs:
        kwargs['confirm'] = "Continue deleting item?"
    kwargs['save_url'] = "%s/%s/edit/%s" % (req.get_app(), res, id)
    kwargs['cancel_url'] = "%s/%s/view/%s" % (req.get_app(), res, id)
    kwargs['delete_url'] = "%s/%s/delete/%s" % (req.get_app(), res, id)
    t = jinja.get_template('tachyonic.ui/view.html')
    resp.body = t.render(**kwargs)


def create(req, resp, id=None, **kwargs):
    res = resource(req)
    if 'config' not in kwargs:
        kwargs['config'] = req.config.get('_empty_')
    kwargs['created_url'] = "%s/%s/create" % (req.get_app(), res)
    kwargs['back_url'] = "%s/%s" % (req.get_app(), res)
    t = jinja.get_template('tachyonic.ui/view.html')
    resp.body = t.render(**kwargs)


@app.resources()
class Tachyon(object):
    def __init__(self):
        router.add(const.HTTP_GET, '/', self.home, 'tachyonic:public')
        router.add(const.HTTP_POST, '/', self.home, 'tachyonic:public')
        router.add(const.HTTP_GET, '/login', self.login, 'tachyonic:public')
        router.add(const.HTTP_POST, '/login', self.login, 'tachyonic:public')
        router.add(const.HTTP_GET, '/logout', self.logout, 'tachyonic:public')
        router.add(const.HTTP_GET, '/expired', self.expired, 'tachyonic:public')

    def logout(self, req, resp):
        clear_session(req)
        render_menus(req)
        router.view('/login', const.HTTP_POST, req, resp)

    def expired(self, req, resp):
        clear_session(req)
        render_menus(req)
        raise exceptions.HTTPBadRequest(title="Authentication", description="Token Expired")

    def home(self, req, resp):
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
