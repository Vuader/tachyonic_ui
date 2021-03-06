from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import json

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino.web.dom import Dom
from tachyonic.neutrino import constants as const
from tachyonic.client import Client

from tachyonic.ui.views import ui

log = logging.getLogger(__name__)


def datatable(req, table_id, url,
              fields, width='100%', view_button=False,
              service=False):
    dom = Dom()
    table = dom.create_element('table')
    table.set_attribute('id', table_id)
    table.set_attribute('class', 'display')
    table.set_attribute('style', "width:%s;" % (width,))

    thead = table.create_element('thead')
    tr = thead.create_element('tr')
    api_fields = []
    for field in fields:
        th = tr.create_element('th')
        th.append(fields[field])
        api_fields.append("%s=%s" % (field, fields[field]))
    if view_button is True:
        th = tr.create_element('th')
        th.append('&nbsp;')
        api_fields.append("%s=%s" % ('id', 'id'))
    id_field_no = len(api_fields) - 1
    api_fields = ",".join(api_fields)

    tfoot = table.create_element('tfoot')
    tr = tfoot.create_element('tr')
    for field in fields:
        th = tr.create_element('th')
        th.append(fields[field])
    if view_button is True:
        th = tr.create_element('th')
        th.append('&nbsp;')

    js = "$(document).ready(function() {"
    js += "var table = $('#%s').DataTable( {" % (table_id,)
    js += "'processing': true,"
    js += "'serverSide': true,"
    js += "'ajax': '%s/dt/?api=%s&fields=%s'" % (req.app, url, api_fields)
    if view_button is True:
        js += ",\"columnDefs\": ["
        js += "{\"targets\": -1,"
        js += "\"data\": null,"
        js += "\"width\": \"26px\","
        js += "\"orderable\": false,"
        js += "\"defaultContent\":"
        js += " '<button class=\"view_button\"></button>'"
        js += "}"
        js += "]"
    js += "} );"
    if view_button is True:
        res = ui.resource(req)
        url = req.get_url()
        js += "$('#%s tbody')" % (table_id,)
        js += ".on( 'click', 'button', function () {"
        js += "var data = table.row( $(this).parents('tr') ).data();"
        if service is False:
            js += "ajax_query(\"#window_content\","
            js += "\"%s/%s/view/\"+data[%s]);" % (req.get_app(), res, id_field_no)
        else:
            js += "ajax_query(\"#service\","
            js += "\"%s/%s/view/\"+data[%s]);" % (req.get_app(), res, id_field_no)
        js += "} );"

    js += "} );"
    script = dom.create_element('script')
    script.append(js)

    return dom.get()


@app.resources()
class DataTables(object):
    def __init__(self):
        router.add(const.HTTP_GET, '/dt', self.dt, 'tachyonic:public')
        router.add(const.HTTP_POST, '/dt', self.dt, 'tachyonic:public')

    def dt(self, req, resp):
        resp.headers['Content-Type'] = const.APPLICATION_JSON
        url = req.query.get('api', [ '' ])
        api_fields = req.query.get('fields', [ '' ])
        api_fields = api_fields[0].split(",")
        draw = req.query.get('draw', [ 0 ])
        start = req.query.get('start', [ 0 ])
        length = req.query.get('length', [ 0 ])
        search = req.query.get('search[value]', [ None ])
        order = req.query.get("order[0][dir]")
        column = req.query.get("order[0][column]")
        count = 0
        orderby = None
        if order is not None and column is not None:
            order = order[0]
            column = column[0]
            for api_field in api_fields:
                if column == str(count):
                    order_field, order_field_name = api_field.split('=')
                    orderby = "%s %s" % (order_field, order)
                count += 1
        api = Client(req.context['restapi'])
        request_headers = {}
        request_headers['X-Pager-Start'] = start[0]
        request_headers['X-Pager-Limit'] = length[0]
        if orderby is not None:
            request_headers['X-Order-By'] = orderby

        if search[0] is not None:
            request_headers['X-Search'] = search[0]
        response_headers, result = api.execute(const.HTTP_GET, url[0],
                                               headers=request_headers)

        recordsTotal = int(response_headers.get('X-Total-Rows',0))
        recordsFiltered = int(response_headers.get('X-Filtered-Rows',0))
        response = {}
        response['draw'] = int(draw[0])
        response['recordsTotal'] = recordsTotal
        response['recordsFiltered'] = recordsFiltered
        data = []
        for row in result:
            fields = []
            for api_field in api_fields:
                field, name = api_field.split("=")
                fields.append(row[field])
            data.append(fields)
        response['data'] = data
        return json.dumps(response, indent=4)
