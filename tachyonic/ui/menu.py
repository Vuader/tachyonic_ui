
from tachyonic import jinja
from tachyonic.neutrino.web.bootstrap3.menu import Menu as NfwMenu


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
        self.items.append([item, link, view])

    def render(self, app, policy, service=False):
        subs = {}
        menu = NfwMenu()
        for item in self.items:
            sub = menu
            item, link, view = item
            if policy.validate(view):
                item = item.strip('/').split('/')
                for (i, l) in enumerate(item):
                    if len(item)-1 == i:
                        if service is True:
                            onclick = "return service(this);"
                            sub.add_link(l, "%s%s" % (app, link),
                                         onclick=onclick)
                        else:
                            onclick = "return admin(this);"
                            sub.add_link(l, "%s%s" % (app, link),
                                         onclick=onclick)
                    else:
                        if l in subs:
                            sub = subs[l]
                        else:
                            s = NfwMenu()
                            subs[l] = s
                            if i == 0:
                                sub.add_dropdown(l, s)
                            else:
                                sub.add_submenu(l, s)
                            sub = s
        if str(menu).strip() == '':
            menu = False
        return menu


admin = Menu()
accounts = Menu()
services = Menu()
