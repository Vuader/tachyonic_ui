from __future__ import absolute_import                                                                            
from __future__ import unicode_literals

import logging
from collections import OrderedDict
import json

from tachyonic import jinja
from tachyonic.neutrino.web.bootstrap3.menu import Menu as NfwMenu

log = logging.getLogger(__name__)

def render_menus(req):
    jinja.request['MENU'] = admin.render(req.app,
                                         req.policy,
                                         False)
    jinja.request['MENU_ACCOUNTS'] = accounts.render(req.app,
                                                     req.policy,
                                                     True)
    jinja.request['MENU_SERVICES'] = services.render(req.app,
                                                     req.policy,
                                                     True)


class Menu():
    def __init__(self):
        self.items = []

    def add(self, item, link, view):
        self.items.append((item, link, view))


    def render(self, app, policy, service=False):
        root = NfwMenu()

        menu_items = OrderedDict()
        # PERMS
        for i in self.items:
            item, link, view = i
            if policy.validate(view):
                item = item.strip('/').split('/')

                def m(items):
                    if len(item) > 1:
                        n = item[0]
                        if n not in items:
                            items[n] = OrderedDict()
                        del item[0]
                        m(items[n])
                    else:
                        n = item[0]
                        if n not in items:
                            items[n] = OrderedDict()
                        items[n]['_name'] = n
                        items[n]['_link'] = link
                        items[n]['_view'] = view

                m = m(menu_items)

        # GENERATE MENU
        def _menu(items, menu, submenu=False):
            subs = {}
            if '_link' in items:
                if service is True:
                    onclick = "return service(this);"
                    menu.add_link(items['_name'], "%s%s" % (app, items['_link']),
                                 onclick=onclick)
                else:
                    onclick = "return admin(this);"
                    menu.add_link(items['_name'], "%s%s" % (app, items['_link']),
                                  onclick=onclick)
            else:
                for i in items:
                        if ('_link' not in items[i] and '_view' not in items[i] and
                                '_name' not in items[i]):
                            if i not in subs:
                                sub = NfwMenu()
                                subs[i] = sub
                            else:
                                sub = subs[i]

                            if submenu is False:
                                menu.add_dropdown(i, sub)
                            else:
                                menu.add_submenu(i, sub)
                        else:
                            sub = menu

                        _menu(items[i], sub, submenu=True)

        _menu(menu_items, root, submenu=False)

        if str(root) == '':
            return None
        else:
            return root
            

admin = Menu()
accounts = Menu()
services = Menu()
