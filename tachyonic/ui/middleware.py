from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from collections import OrderedDict

import tachyonic
from tachyonic.neutrino import constants as const
from tachyonic.common.client import Client
from tachyonic import jinja
from tachyonic.common import exceptions

from tachyonic.ui.auth import clear_session
from tachyonic.ui.auth import authenticated
from tachyonic.ui.menu import render_menus
from tachyonic.ui.views.select import select

log = logging.getLogger(__name__)


class Globals(object):
    def __init__(self, app):
        self.config = app.config
        self.ui_config = app.config.get('ui')
        self.app_config = self.config.get('application')
        tachyonic.jinja.globals['TITLE'] = self.app_config.get('name','Tachyon')
        tachyonic.jinja.globals['NAME'] = self.app_config.get('name')

    def pre(self, req, resp):
        tachyonic.jinja.globals['REQUEST_ID'] = req.request_id
        tachyonic.jinja.globals[''] = self.app_config.get('name','Tachyon')
        req.context['restapi'] = self.ui_config.get('restapi', '')
        resp.headers['Content-Type'] = const.TEXT_HTML


class Auth(object):
    def __init__(self, app):
        pass

    def pre(self, req, resp):
        logout = req.query.get('logout')

        req.context['login'] = False
        req.context['domain_admin'] = False
        req.context['roles'] = []
        req.context['domains'] = []
        tachyonic.jinja.request['LOGIN'] = False

        if logout is not None:
            clear_session(req)

        token = req.session.get('token')
        restapi = req.context['restapi']
        if token is not None:
            api = Client(restapi)
            if req.post.get('domain', None) is not None:
                domain = req.post.get('domain', None)
                req.session['domain'] = domain
            else:
                domain = req.session.get('domain')
            if req.post.get('tenant', None) is not None:
                tenant = req.post.get('tenant', None)
                req.session['tenant'] = tenant
            else:
                tenant = req.session.get('tenant')
            auth = {}
            try:
                auth = api.token(token, domain, tenant)
            except exceptions.ClientError as e:
                clear_session(req)
                raise exceptions.ClientError(e.title,
                                             e.description,
                                             e.status)
            authenticated(req, auth)
            if req.context['login'] is True:
                api_fields = OrderedDict()
                api_fields['id'] = "ID"
                api_fields['name'] = "Name"
                jinja.request['SEARCH'] = select(req, 'search', '/search', api_fields)

        tachyonic.jinja.request['DOMAINS'] = req.context['domains']
        render_menus(req)
