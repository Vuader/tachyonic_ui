# -*- coding: utf-8 -*-
# Copyright (c) 2017, Christiaan Frans Rademan.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging

from tachyonic.neutrino import constants as const
from tachyonic.neutrino.html.dom import Dom
from tachyonic.neutrino.wsgi import app
from tachyonic.neutrino.wsgi import router
from tachyonic.neutrino.wsgi import jinja
from tachyonic.neutrino.client import Client

from tachyonic.api.models.tenants import Tenant as TenantModel

from tachyonic.ui import menu

log = logging.getLogger(__name__)

menu.accounts.add('/View Account', '/tenant', 'tachyonic:login')


@app.resources()
class Tenant(object):
    """ class Tenant

    Adds and process requests to /tenant and /open_tenant routes.

    /tenant is used by the "View Account" Item in the accounts menu.
    /open_tenant is used by the "Open" button in the tenant search results.

    """

    def __init__(self):
        # VIEW TENANT
        router.add(const.HTTP_GET,
                   '/tenant',
                   self.view,
                   'tachyonic:login')
        router.add(const.HTTP_POST,
                   '/tenant',
                   self.view,
                   'tachyonic:login')
        # OPEN TENANT
        router.add(const.HTTP_GET,
                   '/open_tenant',
                   self.view,
                   'tachyonic:public')
        router.add(const.HTTP_POST,
                   '/open_tenant',
                   self.view,
                   'tachyonic:public')

    def view(self, req, resp):
        """Method view(req, resp)

        Used to process requests to /tenant and /open_tenant routes in order
        to display the tenant information.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
        """
        if req.context['login'] is True:
            api = Client(req.context['restapi'])
            server_headers, response = api.execute(const.HTTP_GET, '/v1/tenant')

            if req.is_ajax():
                t = jinja.get_template('tachyonic.ui/view_account.html')
                return t.render(title="Account", content=response)
            else:
                t = jinja.get_template('tachyonic.ui/ajax_wrapper.html')
                return t.render(title="Account", content=response)
        else:
            resp.redirect('/')
