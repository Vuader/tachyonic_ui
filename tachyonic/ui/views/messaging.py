import logging
import json
import time

from tachyonic.neutrino import constants as const
from tachyonic.neutrino.wsgi import app
from tachyonic.neutrino.wsgi import router
from tachyonic.neutrino.timer import timer
from tachyonic.neutrino.wsgi.response import response_io_stream

log = logging.getLogger(__name__)


@app.resources()
class Messaging(object):
    """ class Messaging.

    Adds and process requests to the route /messaging.

    The Tachyonic UI makes periodic requests to /messaging.
    This can be used to display messages to the user of the UI.

    """

    def __init__(self):
        # Add Route
        router.add(const.HTTP_GET, '/messaging', self.get, 'tachyonic:public')

    class Server(object):
        """ class Server

        Creates Object with read() method, which is executed by
        tachyonic.neutrino.wsgi.response.response_io_stream
        so that response is sent to the Browser.
        """

        def __init__(self, req, resp):
            self.req = req
            self.resp = resp
            self.login = True
            self.sent = False
            self.reset = False

        def read(self, size=0):
            """ Method read()

            Executed by tachyonic.neutrino.wsgi.response.response_io_stream
            and response is sent to the Browser.

            Args:
                size (int): Amount of bytes to yield at a time.

            Returns:
                None or json object containing messages for the browser.
            """
            messages = []
            if self.req.context['login'] is False:
                messages.append({'type': 'goto',
                                 'link': self.req.get_app_url() + '/expired'})

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
        """ Method get(req, resp)

        Used to process requests to /messaging in order to provide messages to the browser.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
        """
        req.session.do_not_save()
        server = self.Server(req, resp)
        return response_io_stream(server)
