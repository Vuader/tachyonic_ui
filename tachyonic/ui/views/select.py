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
           url,
           fields,
           css_class=None,
           input_field=None,
           click_url=None,
           service=False):
    dom = Dom()

    i = dom.create_element('input')
    i.set_attribute('id', field_id)

    api_fields = []
    for field in fields:
        api_fields.append("%s=%s" % (field, fields[field]))
    api_fields = ",".join(api_fields)

    js = "$(\"#%s\").autocomplete({" % (field_id,)
    js += "source: '%s/select/?api=%s&fields=%s'," % (req.app, url, api_fields)
    js += "minLength: 3,"
    js += "position: { my : \"right top\", at: \"right bottom\" },"
    #js += "select: function(event, ui) {"
    #js += "var id = ui.item.id;"
    #js += "document.getElementById("$randomId_input").value = id;"
    #js += "},"
    js += "open: function(event, ui) {"
    js += "$(\".ui-autocomplete\").css(\"z-index\", 10000);"
    js += "}"
    #js += "change: function(event, ui) {"
    #js += "if (ui.item === null) {"
    #js += "document.getElementById("$randomId_input").value = "";",
    #js += "document.getElementById("$randomId_search").value = "";",
    #js += "}"
    #js += "}"
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
        url = req.query.get('api', [ '' ])
        api_fields = req.query.get('fields', [ '' ])
        api_fields = api_fields[0].split(",")
        #search = req.query.get('search', [ None ])
        search = req.post.get('term',None)
        api = Client(req.context['restapi'])
        request_headers = {}
        request_headers['X-Pager-Start'] = 0
        request_headers['X-Pager-Limit'] = 25
        request_headers['X-Search'] = search
        response_headers, result = api.execute(const.HTTP_GET, url[0],
                                               headers=request_headers)

        response = []
        for row in result:
            record = {}
            values = []
            for field in row:
                if field == 'id':
                    record['id'] = row[field]
            for api_field in api_fields:
                field, name = api_field.split("=")
                values.append("%s" % (row[field],))
            values = " ".join(values)
            record['value'] = values
            record['label'] = values
            response.append(record)
        return json.dumps(response, indent=4)
