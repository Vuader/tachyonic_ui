import logging
import traceback
from collections import OrderedDict
from copy import deepcopy
import base64
from datetime import datetime

from tachyonic import app
from tachyonic import router
from tachyonic import jinja
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import exceptions
from tachyonic.neutrino import Client
from tachyonic.api.models.themes import Theme as ThemeModel

from tachyonic.ui.views import ui
from tachyonic.ui.views.select import select
from tachyonic.ui.views.datatable import datatable
from tachyonic.ui import menu

from .controllers import default_css

log = logging.getLogger(__name__)

menu.admin.add('/System/Themes', '/themes', 'themes:admin')


@app.resources()
class Themes(object):
    """
    class Themes

    Adds and process requests to the following routes:
        /image...
        /css
        /themes...

    Themes allow one to customize the look and feel of the UI on a per FQDN basis.
    Backgroud Image, logo, Site name and css is customizable.

    /css is used to provide the main stylesheet for the Tachyonic UI.
    """

    def __init__(self):
        # VIEW IMAGES
        router.add(const.HTTP_GET, '/image/{image}', self.images)
        router.add(const.HTTP_GET, '/image/{image}/{theme_id}', self.images)
        # GENERATE CSS
        router.add(const.HTTP_GET, '/css', self.get)
        # VIEW THEMES
        router.add(const.HTTP_GET, '/themes', self.themes, 'themes:admin')
        router.add(const.HTTP_GET, '/themes/view/{theme_id}', self.themes,
                   'themes:admin')
        # CREATE NEW THEME
        router.add(const.HTTP_GET, '/themes/create', self.create,
                   'themes:admin')
        router.add(const.HTTP_POST, '/themes/create', self.create,
                   'themes:admin')
        # MODIFY THEME
        router.add(const.HTTP_GET,
                   '/themes/edit/{theme_id}', self.edit,
                   'themes:admin')
        router.add(const.HTTP_POST,
                   '/themes/edit/{theme_id}', self.edit,
                   'themes:admin')
        # DELETE THEME
        router.add(const.HTTP_GET,
                   '/themes/delete/{theme_id}', self.delete,
                   'themes:admin')

        app_config = app.config.get('application')
        static = app_config.get('static', '').rstrip('/')
        images = "%s/tachyonic.ui/images" % (static,)
        self.css = default_css(images)
        app.context['css'] = self.css

    def images(self, req, resp, image, theme_id=None):
        """ Method images

        Used to process requests to /image/{image} and /image/{image}/{theme_id}
        in order to display background and logo images.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            image (str): Name of the image.
            theme_id (str): Name of the theme if applicable.

        Returns:
            base64 decoded image data.
        """
        api = Client(req.context['restapi'])
        headers, response = api.execute(const.HTTP_GET, "/v1/theme/%s/images" % (theme_id,))
        image_category = None
        image = image.lower()
        if image == 'logo' or image == 'background':
            image_category = image

        if image_category:
            img = response[image_category]
            img_type = response['%s_type' % image_category]
            img_timestamp = response['%s_timestamp' % image_category]
            if img is not None and img != '':
                img = base64.b64decode(img)
                resp.headers['content-type'] = img_type
                resp.modified(datetime.strptime(img_timestamp, "%Y/%m/%d %H:%M:%S"))
                return img

    def themes(self, req, resp, theme_id=None):
        """ Method themes

        Used to process requests to /themes and /themes/view/{theme_id}
        in order to view themes or a particular theme.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            theme_id (str): UUID of the theme if applicable.

        """
        if theme_id is None:
            fields = OrderedDict()
            fields['domain'] = 'Domain'
            fields['name'] = 'Site Name'
            dt = datatable(req, 'themes', '/v1/themes',
                           fields, view_button=True, service=False)
            ui.view(req, resp, content=dt, title='Themes')
        else:
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/v1/theme/%s" % (theme_id,))
            headers, sheet = api.execute(const.HTTP_GET, "/v1/theme/%s/css" %
                                         (theme_id,))

            if response['logo_name'] is not None and response['logo_name'] != '':
                logo = True
            else:
                logo = False

            if response['background_name'] is not None and response['background_name'] != '':
                background = True
            else:
                background = False

            css_t = jinja.get_template('tachyonic.ui/css.html')
            images_t = jinja.get_template('tachyonic.ui/images.html')
            extra = images_t.render(theme_id=theme_id,
                                    background=background,
                                    readonly=True,
                                    logo=logo)
            extra += css_t.render(tags={},
                                  element=None,
                                  sheet=sheet,
                                  theme_id=theme_id,
                                  readonly=True)
            form = ThemeModel(response, validate=False, readonly=True)
            ui.view(req, resp, content=form,
                    id=theme_id, title='View Theme',
                    extra=extra,
                    view_form=True)

    def create(self, req, resp):
        """Method create(req, resp)

        Used to process requests to /themes/create in order to create new themes.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
        """
        if req.method == const.HTTP_POST:
            try:
                form = ThemeModel(req.post, validate=True)
                api = Client(req.context['restapi'])
                headers, response = api.execute(const.HTTP_POST, "/v1/theme", form)
                if 'id' in response:
                    id = response['id']
                    self.themes(req, resp, theme_id=id)
            except exceptions.HTTPBadRequest as e:
                form = ThemeModel(req.post, validate=False)
                ui.create(req, resp, content=form, title='Create Theme', error=[e])
        else:
            form = ThemeModel(req.post, validate=False)
            ui.create(req, resp, content=form, title='Create Theme')

    def delete(self, req, resp, theme_id=None):
        """Method delete(req, resp, theme_id=None)

        Used to process requests to /themes/delete/{theme_id} in order to delete themes.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            theme_id (str): UUID of the particular theme to be deleted.
        """
        api = Client(req.context['restapi'])
        headers, response = api.execute(const.HTTP_DELETE, "/v1/theme/%s" % (theme_id,))
        self.view(req, resp)

    def css_update(self, req, theme_id):
        """ Method css_update(req, theme_id).

        Used by method edit() to update the CSS values.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            theme_id (str): UUID of the theme being worked on.
        """
        api = Client(req.context['restapi'])
        element = req.post.getlist('element')
        delete = req.query.get('delete')
        property = req.post.getlist('property')
        value = req.post.getlist('value')
        url = "/v1/css"
        url += "/%s" % (theme_id,)
        if delete is not None:
            obj = {}
            del_e, del_p = delete.split(",")
            obj['del_element'] = del_e
            obj['del_property'] = del_p
            headers, response = api.execute(const.HTTP_PUT,
                                            url, obj=obj)
        css = []
        for i, e in enumerate(element):
            css.append([e, property[i], value[i]])
            headers, response = api.execute(const.HTTP_PUT,
                                            url, obj=css)

    def images_update(self, req, theme_id):
        """ Method images_update(req, theme_id).

        Used by method edit() to update the logo and background images.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            theme_id (str): UUID of the theme being worked on.
        """
        api = Client(req.context['restapi'])
        url = "/v1/images"
        url += "/%s" % (theme_id,)
        logo = req.post.getfile('logo')
        delete = req.query.get('delete_image')
        background = req.post.getfile('background')
        upload = {}
        images = ["logo", "background"]
        for image in images:
            if eval(image) is not None:
                name, mtype, data = eval(image)
                data = base64.b64encode(data)
                upload[image] = {}
                upload[image]['name'] = name
                upload[image]['type'] = mtype
                upload[image]['data'] = data
        if logo is not None or background is not None:
            headers, response = api.execute(const.HTTP_PUT,
                                            url, obj=upload)
        if delete == "logo" or delete == "background":
            url += "/%s" % delete
            headers, response = api.execute(const.HTTP_DELETE,
                                            url)

    def edit(self, req, resp, theme_id=None):
        """Method edit(req, resp, theme_id=None)

        Used to process requests to /theme/edit/{theme_id} in order to modify themes.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
            theme_id (str): UUID of the particular theme to be modifed.
        """
        save = req.post.get('save', False)
        if req.method == const.HTTP_POST and save is not False:
            form = ThemeModel(req.post, validate=True, readonly=True)
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_PUT, "/v1/theme/%s" %
                                            (theme_id,), form)
            self.css_update(req, theme_id)
            self.images_update(req, theme_id)
        else:
            self.css_update(req, theme_id)
            self.images_update(req, theme_id)
            api = Client(req.context['restapi'])
            headers, response = api.execute(const.HTTP_GET, "/v1/theme/%s" % (theme_id,))
            domain = response['domain']
            form = ThemeModel(response, validate=False)
            if response['logo_name'] is not None and response['logo_name'] != '':
                logo = True
            else:
                logo = False

            if response['background_name'] is not None and response['background_name'] != '':
                background = True
            else:
                background = False

            tags = {}
            for element in self.css:
                tags[element] = element
            css_t = jinja.get_template('tachyonic.ui/css.html')
            images_t = jinja.get_template('tachyonic.ui/images.html')
            element = select(req, 'element', source='tags')
            headers, sheet = api.execute(const.HTTP_GET, "/v1/theme/%s/css" %
                                         (theme_id,))
            extra = images_t.render(theme_id=theme_id,
                                    background=background,
                                    domain=domain,
                                    logo=logo)
            extra += css_t.render(tags=tags,
                                  element=element,
                                  sheet=sheet,
                                  theme_id=theme_id)
            ui.edit(req, resp,
                    content=form,
                    id=theme_id,
                    title='Edit Theme',
                    extra=extra)

    def get(self, req, resp):
        """Method get(req, resp)

        Used to process requests to /css which is the main stylesheet for the Tachyonic web UI.

        Args:
            req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).
            resp (object): Response Object (tachyonic.neutrino.wsgi.response.Response).
        """
        resp.headers['Content-Type'] = const.TEXT_CSS

        sheet = deepcopy(self.css)

        try:
            api = Client(req.context['restapi'])
            headers, custom = api.execute(const.HTTP_GET, "/v1/theme/%s/css" %
                                          (req.get_host(),))
            headers, images = api.execute(const.HTTP_GET, "/v1/theme/%s/images" %
                                          (req.get_host(),))
            if req.context['custom_background'] is True:
                sheet['body']['background-image'] = "url(\"%s/image/background/%s\")" % (req.app, req.get_host())

            for element in custom:
                if element not in sheet:
                    sheet[element] = {}
                for e_property in custom[element]:
                    if custom[element][e_property].strip().lower() == "null":
                        del sheet[element][e_property]
                    else:
                        sheet[element][e_property] = custom[element][e_property]
        except Exception as e:
            trace = str(traceback.format_exc())
            log.error("Unable to retrieve theme %s\n%s" % (e, trace))

        if req.is_mobile():
            sheet['.search-bar-box']['width'] = '100%'
            sheet['.tenant-bar-box']['min-width'] = '100%'

        def css(d, tab=0):
            spacer = "    " * tab
            for v in d:
                if isinstance(d[v], dict):
                    resp.write("%s%s {\n" % (spacer, v,))
                    css(d[v], tab + 1)
                    resp.write("%s}\n\n" % (spacer,))
                else:
                    val = "%s;" % (d[v].rstrip(';'),)
                    resp.write("%s%s: %s\n" % (spacer, v, val))

        css(sheet)
