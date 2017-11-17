# -*- coding: utf-8 -*-
import pytest
import requests
import re
import json

parametrize = pytest.mark.parametrize

app = 'http://localhost/ui'
netrino_app = 'http://localhost/ui/infrastructure/network'
dt = (app + '/dt?api=/infrastructure/network/'
            '%s?view=datatable&fields=id=id'
            '%s&endpoint=netrino_api&order[0][column]=%s'
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


class Netrino:
    def __init__(self):
        self.response = None

    def request(self, req, url, obj=None):
        self.response = requests.request(req,
                                         netrino_app + '/' + url,
                                         data=obj,
                                         cookies={'tachyonic': cookie})

    def dt(self, req, url, search='', fields='', column=0):
        self.response = requests.request(req,
                                         dt % (url, fields, column, search),
                                         cookies={'tachyonic': cookie})


@pytest.fixture
def netrino():
    """Returns a Netrino test object"""
    return Netrino()


igroup_id = None
igroup_params = [
    ('POST', 'igroups/create', {'name': 'unittest'}, 'create'),
    ('GET', 'igroups', {}, 'viewall'),
    ('GET', 'igroups/view/', {}, 'view'),
    ('POST', 'igroups/edit/', {'name': 'unittest-updated'}, 'update')
]


@pytest.mark.parametrize('req, url, obj, test', igroup_params)
def test_igroup(netrino, req, url, obj, test):
    if test == 'create':
        netrino.request(req, url, obj)
        assert netrino.response.status_code == 200
        match = re.search('id="id" value="([^"]+).*value="unittest"', netrino.response.text)
        assert match is not None
        global igroup_id
        igroup_id = match.group(1)
    elif test == 'viewall':
        netrino.dt(req, url, search='unittest')
        assert netrino.response.status_code == 200
        assert json.loads(netrino.response.text)
        response = json.loads(netrino.response.text)
        assert 'recordsTotal' in response
        assert response['recordsTotal'] > 0
    elif test == 'view':
        netrino.request(req, url + igroup_id, obj)
        assert netrino.response.status_code == 200
        assert re.search('edit/' + igroup_id, netrino.response.text)
    elif test == 'update':
        netrino.request(req, url + igroup_id, obj)
        assert netrino.response.status_code == 200


service_id = None


def service(name):
    return {'name': name,
            'user_role': '766E2877-0E06-440A-8E02-E09988FC21A7',
            'config_snippet': name}


service_params = [
    ('POST', 'service/create', service('unittest'), 'create'),
    ('GET', 'services', {}, 'viewall'),
    ('GET', 'service/view/', {}, 'view'),
    ('POST', 'service/edit/', service('unittest-updated'), 'update')
]


@pytest.mark.parametrize('req, url, obj, test', service_params)
def test_service(netrino, req, url, obj, test):
    # We can not return igroup_id via the
    # service() function - somehow global variable
    # is lost inside that function. So we have to
    # add the igroup_id here in this function, but
    # is only required for tests that require obj
    if obj:
        global igroup_id
        obj['interface_group'] = igroup_id
    if test == 'create':
        netrino.request(req, url, obj)
        assert netrino.response.status_code == 200
        match = re.search('edit/([^"]+)" data-name="unit', netrino.response.text)
        assert match is not None
        global service_id
        service_id = match.group(1)
    elif test == 'viewall':
        netrino.dt(req, url, search='unittest')
        assert netrino.response.status_code == 200
        assert json.loads(netrino.response.text)
        response = json.loads(netrino.response.text)
        assert 'recordsTotal' in response
        assert response['recordsTotal'] > 0
    elif test == 'view':
        netrino.request(req, url + service_id, obj)
        assert netrino.response.status_code == 200
        assert re.search('edit/' + service_id, netrino.response.text)
    elif test == 'update':
        netrino.request(req, url + service_id, obj)
        assert netrino.response.status_code == 200


device_ip = '192.0.2.1'
device_id = '3221225985'
device_create_sr = None
device_update_sr = None
device_vals = {'device_ip': device_ip,
               'snmp_community': 'unittest',
               'unittest': True}
device_params = [
    ('POST', 'device/create', device_vals, 'create'),
    ('GET', 'devices', {}, 'viewall'),
    ('GET', 'device/view/', {}, 'view'),
    ('POST', 'device/edit/', device_vals, 'update')
]


@pytest.mark.parametrize('req, url, obj, test', device_params)
def test_device(netrino, req, url, obj, test):
    global device_id
    global device_create_sr
    global device_update_sr
    if test == 'create':
        netrino.request(req, url, obj)
        assert netrino.response.status_code == 200
        assert '/ui/dt?api=/infrastructure/network/devices' in netrino.response.text
        # Creating a Device also creates a service request
        # so we are checking if that also succeeded
        netrino.dt('GET',
                   'service_requests',
                   search=device_id,
                   column=1,
                   fields=',creation_date=creation_date')
        sr_result = json.loads(netrino.response.text)
        assert 'data' in sr_result
        # also need the id for that SR to delete it later
        device_create_sr = sr_result['data'][0][0]
    elif test == 'viewall':
        netrino.dt(req, url, search='unittest')
        assert netrino.response.status_code == 200
        assert json.loads(netrino.response.text)
        response = json.loads(netrino.response.text)
        assert 'recordsTotal' in response
        assert response['recordsTotal'] > 0
    elif test == 'view':
        netrino.request(req, url + device_id, obj)
        assert netrino.response.status_code == 200
        assert re.search('edit/' + device_id, netrino.response.text)
    elif test == 'update':
        netrino.request(req, url + device_id, obj)
        assert netrino.response.status_code == 200
        netrino.dt('GET',
                   'service_requests',
                   search=device_id,
                   column=1,
                   fields=',creation_date=creation_date')
        sr_result = json.loads(netrino.response.text)
        assert 'data' in sr_result
        # also need the id for that SR to delete it later
        device_update_sr = sr_result['data'][0][0]


# Service requests needs to be associated to a tenant
# In order to test creation of a service request
# we thus first have to create a tenant, and then
# open that tenant

tenant_id = None
cookie = "bla"


def test_create_tenant():
    tenant_vals = {"name": "unittest",
                   "email": "un@te.st",
                   "enabled": "on"}
    r = requests.request("POST",
                         app + "/tenants/create",
                         data=tenant_vals,
                         cookies={'tachyonic': cookie})
    assert r.status_code == 200
    match = re.search('value="([^"]+)" id="id".*value="unittest"', r.text)
    assert match is not None
    global tenant_id
    tenant_id = match.group(1)


def test_open_tenant():
    r = requests.request("POST",
                         app + "/open_tenant",
                         data={"X-Tenant-Id": tenant_id},
                         cookies={'tachyonic': cookie})
    assert r.status_code == 200


service_request_id = None
# We can get the correct device_id here in global
# but the service_id we will only get inside the
# function
service_request_vals = {"device": device_id,
                        "service": service_id}
service_request_params = [
    ('POST', 'sr/create', service_request_vals, 'create'),
    ('GET', 'service_requests', {}, 'viewall'),
    ('GET', 'sr/view/', {}, 'view'),
    ('GET', 'sr/edit/', {}, 'activate'),
    ('GET', 'sr/edit/', {}, 'deactivate')
]


@pytest.mark.parametrize('req, url, obj, test', service_request_params)
def test_service_request(netrino, req, url, obj, test):
    global device_id
    global service_request_id
    if obj:
        global service_id
        obj["service"] = service_id
    if test == 'create':
        netrino.request(req, url, obj)
        assert netrino.response.status_code == 200
        assert '/ui/dt?api=/infrastructure/network/service_requests' in netrino.response.text
    elif test == 'viewall':
        netrino.dt(req,
                   url,
                   column=1,
                   fields=',creation_date=creation_date',
                   search="unittest")
        assert netrino.response.status_code == 200
        assert json.loads(netrino.response.text)
        response = json.loads(netrino.response.text)
        assert 'recordsTotal' in response
        assert response['recordsTotal'] > 0
        service_request_id = response['data'][0][0]
    elif test == 'view':
        netrino.request(req, url + service_request_id, obj)
        assert netrino.response.status_code == 200
        assert re.search('PENDING', netrino.response.text)
    elif test == 'activate':
        netrino.request(req,
                        url + service_request_id + '/activate',
                        obj)
        assert netrino.response.status_code == 200
        assert re.search('ACTIVE', netrino.response.text)
    elif test == 'deactivate':
        netrino.request(req,
                        url + service_request_id + '/deactivate',
                        obj)
        assert netrino.response.status_code == 200
        assert re.search('INACTIVE', netrino.response.text)


cleanup_params = [('GET', 'igroups/delete/'),
                  ('GET', 'service/delete/'),
                  ('GET', 'device/delete/'),
                  ('GET', 'sr/delete/'),
                  ('GET', 'sr/delete/'),
                  ('GET', 'sr/delete/')]


# we have 3 service requests to delete:
# the two for the device creation and update
# as well as the one created during the
# service_requests creation test


@pytest.mark.parametrize('req, url', cleanup_params)
def test_cleanup(netrino, req, url):
    if 'igroup' in url:
        global igroup_id
        id = igroup_id
    elif 'service/' in url:
        global service_id
        id = service_id
    elif 'device' in url:
        global device_id
        id = device_id
    elif 'sr/delete' in url:
        global device_create_sr
        global device_update_sr
        if device_create_sr:
            id = device_create_sr
            device_create_sr = None
        elif device_update_sr:
            id = device_update_sr
            device_update_sr = None
        else:
            global service_request_id
            id = service_request_id
    netrino.request(req, url + id, {})
    assert netrino.response.status_code == 200


def test_cleanup_tenant():
    r = requests.request('GET',
                         app + '/tenants/delete/' + tenant_id,
                         cookies={'tachyonic': cookie},
                         headers={"X-Tenant-Id": ""})
    assert r.status_code == 200
