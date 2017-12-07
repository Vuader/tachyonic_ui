import logging

from tachyonic.neutrino.wsgi import jinja

log = logging.getLogger(__name__)


def authenticated(req, auth):
    """
    Function used by Tachyonic ui login method
    to update the session and context in the
    request once user is authenticated

    Args:
        req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
        auth (dict): Dictionary returned by the login/authenticate method.
    """
    if req.session.get('token') is not None:
        jinja.request['LOGIN'] = True
        req.context['roles'] = []
        req.context['domain_admin'] = False
        req.context['domains'] = []
        jinja.request['USERNAME'] = auth['username']
        jinja.request['EMAIL'] = auth['email']
        # In case any of these have changed, we update
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
    """
    Function used by Tachyonic ui and middleware to
    clear all session and context values in the request
    object in the case where login was unsuccessful

    :param req: Request object
    """
    req.session.clear()
    req.context['login'] = False
    req.context['domain_admin'] = False
    req.context['domains'] = []
    req.context['roles'] = []
    jinja.request['LOGIN'] = False
