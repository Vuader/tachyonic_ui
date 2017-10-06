from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import traceback
from collections import OrderedDict

from tachyonic import app
from tachyonic import jinja
from tachyonic.common import constants as const
from tachyonic.client.middleware import Token
from tachyonic.common import exceptions
from tachyonic.client import Client

from tachyonic.ui import html_assets
from tachyonic.ui.auth import clear_session
from tachyonic.ui.menu import render_menus
from tachyonic.ui.views.select import select

log = logging.getLogger(__name__)


class Globals(object):
    def __init__(self):
        self.config = app.config
        self.ui_config = app.config.get('ui')
        self.app_config = self.config.get('application')
        jinja.globals['NAME'] = self.app_config.get('name', 'Tachyon UI')

    def pre(self, req, resp):
        try:
            if app.config.get("tachyon").get("restapi") is None:
                raise exceptions.HTTPInternalServerError('settings.cfg',
                                                         'Missing [tachyon] restapi')
            req.context['restapi'] = app.config.get("tachyon").get("restapi","http://127.0.0.1")
            api = Client(req.context['restapi'])
            headers, theme = api.execute(const.HTTP_GET, "/v1/theme/%s/single" %
                                          (req.get_host(),))
            if 'background' in theme:
                req.context['custom_background'] = theme['background']
            else:
                req.context['custom_background'] = None

            if 'logo' in theme:
                req.context['custom_logo'] = theme['logo']
            else:
                req.context['custom_logo'] = None
            if 'name' in theme:
                jinja.request['NAME'] = theme['name']
            if 'logo' in theme:
                jinja.request['CUSTOM_LOGO'] = theme['logo']
            jinja.request['THEME_DOMAIN'] = req.get_host()
        except Exception as e:
            trace = str(traceback.format_exc())
            log.error("Unable to retrieve theme %s\n%s" % (e, trace))
        jinja.request['REQUEST_ID'] = req.request_id
        jinja.globals['HTML_ASSETS'] = html_assets.render(req)


class Auth(Token):
    def pre(self, req, resp):
        try:
            self.interface = 'ui'
            if req.view is not None:
                super(Auth, self).pre(req, resp)
                resp.headers['Content-Type'] = const.TEXT_HTML
        except exceptions.ClientError as e:
            resp.headers['Content-Type'] = const.TEXT_HTML
            if e.status != const.HTTP_500:
                clear_session(req)
                self.init(req, resp)
                raise exceptions.Authentication(e)
            else:
                self.init(req, resp)
                raise exceptions.HTTPInternalServerError("RESTAPI Offline %s" % e.title, e)

    def init(self, req, resp):
        if req.context['domain_admin'] is False:
            if req.context['tenant_id'] is None:
                if len(req.context['tenants']) > 0:
                    log.error(req.context['tenants'][0][0])
                    api = Client(req.context['restapi'])
                    req.context['tenant_id'] = req.context['tenants'][0][0]
                    api.tenant(req.context['tenant_id'])
        logout = req.query.get('logout')
        jinja.request['LOGIN'] = False
        if 'token' in req.session:
            req.context['login'] = True
        jinja.request['USERNAME'] = req.context['username']
        req.session['tenant_id'] = req.context['tenant_id']
        req.session['domain'] = req.context['domain_id']
        jinja.request['IS_ROOT'] = req.context['is_root']
        jinja.request['DOMAIN'] = req.context['domain']
        jinja.request['DOMAIN_ID'] = req.context['domain_id']
        jinja.request['EMAIL'] = req.context['email']
        jinja.request['DOMAINS'] = req.context['domains']
        jinja.request['ROLES'] = req.context['roles']
        if logout is not None:
            clear_session(req)
        elif req.context['login'] is True:
            jinja.request['LOGIN'] = True
            api_fields = OrderedDict()
            api_fields['id'] = "ID"
            api_fields['name'] = "Name"
            select_js = """
            $("#search").val(ui.item.label);
            $("#searchForm").submit();
            """
            jinja.request['SEARCH'] = select(req, 'search', '/v1/search',
                                             api_fields,
                                             select=select_js,
                                             placeholder="Tenant Name",
                                             keywords_mode=True)
        else:
            clear_session(req)
        render_menus(req)

    def post(self, req, resp):
        if hasattr(req.context, 'login') and req.context['login'] is False:
            req.session.clear()
