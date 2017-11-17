import logging

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino.web.dom import Dom
from tachyonic.neutrino import Client
from tachyonic.neutrino.timer import timer as nfw_timer

from tachyonic.api.models.tenants import Tenant as TenantModel

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
        t = nfw_timer()
        api = Client(req.context['restapi'])
        search = req.post.get('search')
        request_headers = {}
        request_headers['X-Search'] = search
        request_headers['X-Order-By'] = 'name desc'
        dom = Dom()
        searchfor = dom.create_element('H1')
        searchfor.append("Searching for <i><u>%s</u></i>" % (search,))

        response_headers, result = api.execute(const.HTTP_GET, '/v1/search',
                                               headers=request_headers)
        for r in result:
            item = dom.create_element('div')
            item.set_attribute('class', 'search_result')
            form = item.create_element('form')
            form.set_attribute('method', 'post')
            form.set_attribute('action', "%s/open_tenant" % req.app)
            title = form.create_element('div')
            title.set_attribute('class', 'search_title')
            ids = item.create_element('div')
            ids.set_attribute('class','ids')
            info = item.create_element('div')

            dm = TenantModel(data=r, validate=False,
                             readonly=True, cols=2)
            title.append(dm['name'])
            enter = title.create_element("input")
            enter.set_attribute("class", "btn btn-space btn-xs btn-warning")
            enter.set_attribute("type", "submit")
            enter.set_attribute("value", "Open")
            tenant_id = form.create_element('input')
            tenant_id.set_attribute('type','hidden')
            tenant_id.set_attribute('name','X-Tenant-Id')
            tenant_id.set_attribute('value',r['id'])

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
                        info.append("<B>%s:</B> " % (field.label,))
                        if str(field.value()).lower() in search.lower():
                            info.append("<span class=\"red\"><I><U>%s</U></I></span>" % (field.value(),))
                        elif search.lower() in str(field.value()).lower():
                            info.append("<span class=\"red\"><I><U>%s</U></I></span>" % (field.value(),))
                        else:
                            info.append("<I>%s</I>" % (field.value(),))
                        info.append(" ")
        found = dom.create_element('H1')
        found = found.create_element('I')
        found.append("<H3>Results found %s in %s seconds</H3>" % (len(result),
                                                          nfw_timer(t)))
           
        return dom.get()
