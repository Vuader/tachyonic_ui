from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from collections import OrderedDict

from tachyonic import jinja

log = logging.getLogger(__name__)


def authenticated(req, auth):
    if req.session.get('token') is not None:
        jinja.request['LOGIN'] = True
        req.context['roles'] = []
        req.context['domain_admin'] = False
        req.context['domains'] = []
        jinja.request['USERNAME'] = auth['username']
        jinja.request['EMAIL'] = auth['email']
        if 'token' in req.session:
            req.session['token'] = req.session['token']
        if 'domain' in req.session:
            req.session['domain'] = req.session['domain']
        if 'tenant' in req.session:
            req.session['tenant'] = req.session['tenant']

        for r in auth['roles']:
            if r['domain_name'] not in req.context['domains']:
                req.context['domains'].append(r['domain_name'])
            req.context['roles'].append(r['role_name'])
            if r['domain_name'] == req.session.get('domain'):
                if r['tenant_id'] is None:
                    req.context['domain_admin'] = True
        req.context['login'] = True
    else:
        clear_session(req)


def clear_session(req):
    if 'token' in req.session:
        del req.session['token']
    if 'domain_id' in req.session:
        del req.session['domain_id']
    if 'tenant_id' in req.session:
        del req.session['tenant_id']
    req.context['login'] = False
    req.context['domain_admin'] = False
    req.context['domains'] = []
    req.context['roles'] = []
    jinja.request['LOGIN'] = False
