from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino.web.dom import Dom
from tachyonic.client import Client

from tachyonic.ui.models.tenants import Tenant as TenantModel

log = logging.getLogger(__name__)


@app.resources()
class Search(object):
    def __init__(self):
        # VIEW USERS
        router.add(const.HTTP_GET,
                   '/search',
                   self.search,
                   'tachyonic:login')
        router.add(const.HTTP_POST,
                   '/search',
                   self.search,
                   'tachyonic:login')

    def search(self, req, resp):
        api = Client(req.context['restapi'])
        search = req.post.get('search')
        request_headers = {}
        request_headers['X-Search'] = search
        dom = Dom()
        searchfor = dom.create_element('div')
        searchfor.append("Searching for %s" % (search,))

        response_headers, result = api.execute(const.HTTP_GET, '/v1/search',
                                               headers=request_headers)
        for r in result:
            item = dom.create_element('div')
            item.set_attribute('class', 'search_result')
            title = item.create_element('div')
            title.set_attribute('class', 'search_title')
            ids = item.create_element('div')
            ids.set_attribute('class','ids')
            info = item.create_element('div')

            dm = TenantModel(r, validate=False,
                             readonly=True, cols=2)
            title.append(dm['name'])
            enter = title.create_element("a")
            enter.set_attribute("class", "btn btn-space btn-xs btn-warning")
            enter.append("Open")
            enter.set_attribute('data-url', "%s/tenant" % req.get_app_url())
            enter.set_attribute('data-name', 'View Account')
            ids.append('<B>Tenant ID</B> ')
            ids.append(dm['id'])
            ids.append(' <B>External ID</B> ')
            ids.append(dm['external_id'])
            for f in dm._declared_fields:
                field = dm[f]
                if (field.value() is not None and
                        str(field.value()).strip() != '' and
                        field.label is not None):
                    if (f != 'id' and f != 'external_id' and
                            f != 'name'):
                        info.append("%s" % (field.label,))
                        info.append(" ")
                        if str(field.value()).lower() == search.lower():
                            info.append("<B>%s</B>" % (field.value,))
                        else:
                            info.append("<I>%s</I>" % (field.value(),))
                        info.append(" ")

        return dom.get()
