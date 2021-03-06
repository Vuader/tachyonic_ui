from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import json
import time

from tachyonic import app
from tachyonic import router

log = logging.getLogger(__name__)
from tachyonic.neutrino import constants as const
from tachyonic.neutrino.utils.general import timer as nfw_timer
from tachyonic.neutrino.response import response_io_stream


@app.resources()
class Messaging(object):
    def __init__(self):
        router.add(const.HTTP_GET, '/messaging', self.get, 'tachyonic:public')

    class Server(object):
        def __init__(self, req, resp):
            self.req = req
            self.resp = resp
            self.login = True
            self.sent = False
            self.timer = nfw_timer()
            self.reset = False

        def read(self, size=0):
            messages = []
            if self.req.context['login'] is False:
                messages.append({'type': 'goto',
                                 'link': self.req.get_app_url()+'/expired' })

            while True:
                time.sleep(1)
                if nfw_timer(self.timer) > 50:
                    self.reset = True
                    self.timer = nfw_timer()
                    return "[]"

                if self.sent is True or self.reset is True:
                    return None
                else:
                    if len(messages) > 0:
                        self.sent = True
                        return json.dumps(messages, indent=4)

    def get(self, req, resp):
        server = self.Server(req, resp)
        return response_io_stream(server)
