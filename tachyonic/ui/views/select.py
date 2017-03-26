from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import json

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino.web.dom import Dom
from tachyonic.neutrino import constants as const
from tachyonic.client import Client

log = logging.getLogger(__name__)


def select(req,
           field_id,
           url=None,
           fields=None,
           css_class=None,
           input_field=None,
           click_url=None,
           keywords_mode=False,
           placeholder=None,
           select=None,
           change=None,
           source=None,
           service=False):
    dom = Dom()

    i = dom.create_element('input')
    i.set_attribute('id', field_id)
    i.set_attribute('name', field_id)
    i.set_attribute('class', 'form-control')
    if placeholder is not None:
        i.set_attribute('placeholder', placeholder)

    api_fields = []
    if fields is not None:
        for field in fields:
            api_fields.append("%s=%s" % (field, fields[field]))

        api_fields = ",".join(api_fields)

    js = "$(\"#%s\").autocomplete({" % (field_id,)
    if source is not None:
        js += "source: %s," % source
    elif keywords_mode is True:
        js += "source: '%s/select/?api=%s&fields=%s&keywords_mode=1'," % (req.app, url, api_fields)
    else:
        js += "source: '%s/select/?api=%s&fields=%s'," % (req.app, url, api_fields)

    js += "minLength: 3,"
    js += "position: { my : \"right top\", at: \"right bottom\" },"
    if select is not None:
        js += "select: function(event, ui) {"
        js += select
        js += "},"
    if change is not None:
        js += "change: function(event, ui) {"
        js += change
        js += "},"
    js += "open: function(event, ui) {"
    js += "$(\".ui-autocomplete\").css(\"z-index\", 10000);"
    js += "}"
    js += "});"

    s = dom.create_element('script')
    s.append(js)

    return str(dom.get())


@app.resources()
class Select(object):
    def __init__(self):
        router.add(const.HTTP_GET, '/select', self.select, 'tachyonic:public')
        router.add(const.HTTP_POST, '/select', self.select, 'tachyonic:public')

    def select(self, req, resp):
        resp.headers['Content-Type'] = const.APPLICATION_JSON
        url = req.query.getlist('api', [ '' ])
        api_fields = req.query.getlist('fields', [ '' ])
        api_fields = api_fields[0].split(",")
        #search = req.query.getlist('search', [ None ])
        search = req.post.get('term',None)
        api = Client(req.context['restapi'])
        request_headers = {}
        request_headers['X-Pager-Start'] = 0
        request_headers['X-Pager-Limit'] = 25
        request_headers['X-Search'] = search
        response_headers, result = api.execute(const.HTTP_GET, url[0],
                                               headers=request_headers)

        response = []
        if 'keywords_mode' in req.post:
            for row in result:
                # DONT USE ONE FOR.. ID could come only later...
                for field in row:
                    if field == 'id':
                        id = row[field]
                for api_field in api_fields:
                    field, name = api_field.split("=")
                    if row[field] is not None:
                        if search.lower() in row[field].lower():
                            record = {}
                            record['id'] = id
                            record['label'] = row[field]
                            record['value'] = row[field]
                            response.append(record)

        else:
            for row in result:
                record = {}
                values = []
                for field in row:
                    if field == 'id':
                        record['id'] = row[field]

                for api_field in api_fields:
                    field, name = api_field.split("=")
                    record[field] = row[field]
                    if name is not None and name != 'None':
                        values.append("%s" % (row[field],))
                values = " ".join(values)
                record['value'] = values
                record['label'] = values
                response.append(record)
        return json.dumps(response, indent=4)
