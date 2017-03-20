from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from collections import OrderedDict

from tachyonic import app
from tachyonic import jinja
from tachyonic.neutrino import constants as const
from tachyonic.client.middleware import Token
from tachyonic.client import exceptions

from tachyonic.ui.auth import clear_session
from tachyonic.ui.menu import render_menus
from tachyonic.ui.views.select import select

log = logging.getLogger(__name__)


class Globals(object):
    def __init__(self):
        self.config = app.config
        self.ui_config = app.config.get('ui')
        self.app_config = self.config.get('application')
        jinja.globals['TITLE'] = self.app_config.get('name','Tachyon')
        jinja.globals['NAME'] = self.app_config.get('name')

    def pre(self, req, resp):
        jinja.globals['REQUEST_ID'] = req.request_id
        resp.headers['Content-Type'] = const.TEXT_HTML


class Auth(Token):
    def pre(self, req, resp):
        try:
            super(Auth, self).pre(req, resp)
        except exceptions.ClientError:
            clear_session(req)


    def init(self, req):
        logout = req.query.get('logout')
        jinja.request['LOGIN'] = False
        jinja.request['USERNAME'] = req.context['username']
        jinja.request['EMAIL'] = req.context['email']
        jinja.request['DOMAINS'] = req.context['domains']
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
                                             placeholder="Customer Name",
                                             keywords_mode=True)
        else:
            clear_session(req)
        render_menus(req)
