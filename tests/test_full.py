# -*- coding: utf-8 -*-
import pytest
import requests
import re
import json
from functions import get_form_value

parametrize = pytest.mark.parametrize

app = 'http://localhost/ui'
dt = (app + '/dt?api=/v1/%s&fields=id=id%s&order[0][column]=%s'
            '&order[0][dir]=desc&length=1&search[value]=%s')


def test_login_pass():
    r = requests.post(app + "/login",
                      data={'username': 'root', 'password': 'password'})
    assert r.status_code == 200

    # "'tachyonic' in r.cookies" works on regular installs,
    # but not when running in docker container on localhost.
    # Sow now we first have to do the following as a workaround:
    assert 'Set-Cookie' in r.headers
    set_cookie = r.headers.get('Set-Cookie').split(';')
    tachyonic_cookie = set_cookie[0]
    assert 'tachyonic=' in tachyonic_cookie
    tcookie = tachyonic_cookie.split('=')[1]
    r = requests.post(app + "/login",
                      data={'username': 'root', 'password': 'password'},
                      cookies={'tachyonic': tcookie})

    assert 'tachyonic' in r.cookies
    global cookie
    cookie = r.cookies['tachyonic']
    assert re.search('(Username.*\n.*\n.*root)', r.text)


class Tachyonic:
    def __init__(self):
        self.response = None

    def request(self, req, url, obj=None):
        self.response = requests.request(req,
                                         app + '/' + url,
                                         data=obj,
                                         cookies={'tachyonic': cookie})

    def dt(self, req, url, search='', fields='', column=0):
        self.response = requests.request(req,
                                         dt % (url, fields, column, search),
                                         cookies={'tachyonic': cookie})


@pytest.fixture
def tachyonic():
    """Returns a tachyonic test object"""
    return Tachyonic()


ids = {'user': '',
       'role': '',
       'domain': '',
       'tenant': ''}

crud_params = [
    ('user', 'username', {'password': 'Password1'}, 'create'),
    ('role', 'name', {}, 'create'),
    ('domain', 'name', {}, 'create'),
    ('tenant', 'name', {'enabled': 'on'}, 'create'),
    ('user', 'user_id', {'role': 'unittest'}, 'assign'),
    ('user', 'username', {'password': 'Password1'}, 'edit'),
    ('role', 'name', {}, 'edit'),
    ('domain', 'name', {}, 'edit'),
    ('tenant', 'name', {}, 'edit'),
    ('user', None, None, 'view'),
    ('role', None, None, 'view'),
    ('domain', None, None, 'view'),
    ('tenant', None, None, 'view'),
    ('user', None, None, 'delete'),
    ('role', None, None, 'delete'),
    ('domain', None, None, 'delete'),
    ('tenant', None, None, 'delete')
]

@pytest.mark.parametrize('model, field, obj, action', crud_params)
def test_crud(tachyonic, model, field, obj, action):
    global ids
    #First prepare the request:
    if action == 'create':
        obj[field] = "unittest"
        req = 'POST'
    elif action == 'assign':
        action = 'edit'
        obj[field] = ids['user'][1:]
        obj['assign_domain_id'] = ids['domain'][1:]
        req = 'POST'
    elif action == 'edit':
        obj[field] = "unittestmodfd"
        obj['id'] = ids[model][1:]
        obj['save'] = True
        req = 'POST'
    elif action == 'view':
        req = 'GET'
    elif action == 'delete':
        req = 'GET'

    # Then perform the request
    tachyonic.request(req, '%ss/%s%s' % (model, action, ids[model]), obj)
    assert tachyonic.response.status_code == 200

    # Lastly some more checks to see if we got what we wanted
    if action == 'create':
        id = get_form_value('id', tachyonic.response.text)
        assert id is not None
        ids[model] = '/' + id
        match = re.search(obj[field], tachyonic.response.text)
        assert match is not None
    elif action == 'edit':
        # When we POST/save on edit, response is 200 empty
        # and leaves us on the edit form.
        # To see if our change really had effect (in addition
        # to 200, we look for it in the datatables list
        tachyonic.dt('GET', model + 's', search='unittest')
        assert tachyonic.response.status_code == 200
        assert json.loads(tachyonic.response.text)
        response = json.loads(tachyonic.response.text)
        assert 'recordsTotal' in response
        assert response['recordsTotal'] > 0
    elif action == 'view':
        # In addition to 200, let's see if we
        # at least got non-empty response
        # that has our ID in it
        match = re.search(ids[model][1:],tachyonic.response.text)
        assert match is not None
    elif action == 'delete':
        # In addition to 200, let's see if we
        # our entry is really gone
        # that has our ID in it
        tachyonic.request(req, '%ss/%s%s' % (model, 'view', ids[model]), obj)
        assert tachyonic.response.status_code == 404


    # TODO: test role assignment
