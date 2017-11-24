import logging
import json
import time

from tachyonic import app
from tachyonic import router
from tachyonic.neutrino import constants as const
from tachyonic.neutrino.timer import timer
from tachyonic.neutrino.wsgi.response import response_io_stream

log = logging.getLogger(__name__)


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
            self.reset = False

        def read(self, size=0):
            messages = []
            if self.req.context['login'] is False:
                messages.append({'type': 'goto',
                                 'link': self.req.get_app_url()+'/expired' })

            with timer() as elapsed:
                while True:
                    time.sleep(1)
                    if elapsed() > 50:
                        self.reset = True
                        return "[]"

                    if self.sent is True or self.reset is True:
                        return None
                    else:
                        if len(messages) > 0:
                            self.sent = True
                            return json.dumps(messages, indent=4)

    def get(self, req, resp):
        req.session.do_not_save()
        server = self.Server(req, resp)
        return response_io_stream(server)
