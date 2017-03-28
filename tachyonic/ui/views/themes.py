from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import traceback
from collections import OrderedDict
from copy import deepcopy
import base64

from tachyonic import app
from tachyonic import router
from tachyonic import jinja
from tachyonic.neutrino import constants as const
from tachyonic.neutrino import exceptions
from tachyonic.client import Client

from tachyonic.ui.views import ui
from tachyonic.ui.views.select import select
from tachyonic.ui.views.datatable import datatable
from tachyonic.ui.models.themes import Theme as ThemeModel
from tachyonic.ui import menu

log = logging.getLogger(__name__)

menu.admin.add('/System/Themes','/themes','themes:admin')

@app.resources()
class Themes(object):
    def __init__(self):
        router.add(const.HTTP_GET, '/image/{image}', self.images)
        router.add(const.HTTP_GET, '/image/{theme_id}/{image}', self.images)
        router.add(const.HTTP_GET, '/css', self.get)
        router.add(const.HTTP_GET, '/themes', self.themes, 'themes:admin')
        router.add(const.HTTP_GET, '/themes/view/{theme_id}', self.themes,
                   'themes:admin')
        router.add(const.HTTP_GET, '/themes/create', self.create,
                   'themes:admin')
        router.add(const.HTTP_POST, '/themes/create', self.create,
                   'themes:admin')
        router.add(const.HTTP_GET,
                   '/themes/edit/{theme_id}', self.edit,
                   'themes:admin')
        router.add(const.HTTP_POST,
                   '/themes/edit/{theme_id}', self.edit,
                   'themes:admin')
        # DELETE USERS
        router.add(const.HTTP_GET,
                   '/themes/delete/{theme_id}', self.delete,
                   'themes:admin')

        app_config = app.config.get('application')
        static = app_config.get('static', '').rstrip('/')
        images = "%s/tachyonic.ui/images" % (static,)
        self.css = OrderedDict()
        app.context['css'] = self.css
        self.css['.modal-body'] = {}
        self.css['.modal-body']['overflow-y'] = 'scroll'
        self.css['.navbar-wrapper'] = {}
        self.css['.navbar-wrapper']['box-shadow'] = '0 5px 15px rgba(0, 0, 0, .5)'
        self.css['.modal-header'] = {}
        self.css['.modal-header']['background-color'] = "#98AFC7"
        self.css['.modal-header']['border-bottom'] = "1px solid #000"
        self.css['.red'] = {}
        self.css['.red']['color'] = 'red'
        self.css['body'] = {}
        self.css['body']['background-color'] = '#E7E8EB'
        self.css['body']['background-image'] = "url(\"%s/bg.jpg\")" % images
        self.css['body']['background-repeat'] = 'no-repeat'
        self.css['body']['background-size'] = '100% 100%'
        self.css['body']['background-attachment'] = 'fixed'
        self.css['body']['margin-bottom'] = '0px'
        self.css['body']['margin-left'] = '0px'
        self.css['body']['margin-right'] = '0px'
        self.css['body']['margin-top'] = '0px'
        self.css['.btn-space'] = {}
        self.css['.btn-space']['margin-left'] = '5px'
        self.css['.btn-space']['margin-right'] = '5px'
        self.css['.modal-dialog'] = {}
        self.css['.modal-dialog']['width'] = '75%'
        self.css['button.view_button'] = {}
        view_button = self.css['button.view_button']
        view_button['height'] = '24px'
        view_button['width'] = '24px'
        view_button['border-width'] = '1px'
        view_button['background-color'] = '#FFFFFF'
        view_button['background-image'] = "url(\"%s/view.png\")" % images
        view_button['background-repeat'] = 'no-repeat'
        view_button['border-style'] = 'solid'
        self.css['button.edit_button'] = {}
        edit_button = self.css['button.edit_button']
        edit_button['height'] = '24px'
        edit_button['width'] = '24px'
        edit_button['border-width'] = '1px'
        edit_button['background-color'] = '#FFFFFF'
        edit_button['background-image'] = "url(\"%s/edit.png\")" % (images,)
        edit_button['border-style'] = 'solid'
        edit_button['background-repeat'] = 'no-repeat'
        self.css['.menu-icon'] = {}
        self.css['.menu-icon']['padding-top'] = '0px'
        self.css['.menu-icon']['padding-bottom'] = '0px'
        self.css['.menu-icon']['opacity'] = '0.5'
        self.css['.menu-icon:hover'] = {}
        self.css['.menu-icon:hover']['opacity'] = '1'
        self.css['div.locked'] = {}
        self.css['div.locked']['display'] = 'none'
        self.css['div.locked']['background-color'] = '#000000'
        self.css['div.locked']['overflow'] = 'hidden'
        self.css['div.locked']['position'] = 'fixed'
        self.css['div.locked']['z-index'] = '1050'
        self.css['div.locked']['top'] = '0'
        self.css['div.locked']['left'] = '0'
        self.css['div.locked']['height'] = '100%'
        self.css['div.locked']['width'] = '100%'
        self.css['div.locked']['opacity'] = '0.4'
        self.css['div.confirm'] = {}
        self.css['div.confirm']['display'] = 'none'
        self.css['div.confirm']['position'] = 'absolute'
        self.css['div.confirm']['top'] = '100px'
        self.css['div.confirm']['left'] = '10%'
        self.css['div.confirm']['right'] = '10%'
        self.css['div.confirm']['margin'] = 'auto'
        self.css['div.confirm']['width'] = '600px'
        self.css['div.confirm']['height'] = 'auto'
        self.css['div.confirm']['background-color'] = '#FFFFFF'
        self.css['div.confirm']['z-index'] = '10000'
        self.css['div.confirm']['overflow'] = 'auto'
        self.css['div.confirm']['border'] = '1px solid rgba(0, 0, 0, .2)'
        self.css['div.confirm']['border-radius'] = '6px'
        self.css['div.confirm']['box-shadow'] = '0 5px 15px rgba(0, 0, 0, .5)'
        self.css['div.auto-logout'] = {}
        self.css['div.auto-logout']['display'] = 'none'
        self.css['div.auto-logout']['position'] = 'absolute'
        self.css['div.auto-logout']['top'] = '100px'
        self.css['div.auto-logout']['left'] = '10%'
        self.css['div.auto-logout']['right'] = '10%'
        self.css['div.auto-logout']['margin'] = 'auto'
        self.css['div.auto-logout']['width'] = '1000px'
        self.css['div.auto-logout']['height'] = 'auto'
        self.css['div.auto-logout']['background-color'] = '#FFFFFF'
        self.css['div.auto-logout']['z-index'] = '1005'
        self.css['div.auto-logout']['overflow'] = 'auto'
        self.css['div.auto-logout']['border'] = '1px solid rgba(0, 0, 0, .2)'
        self.css['div.auto-logout']['border-radius'] = '6px'
        self.css['div.auto-logout']['box-shadow'] = '0 5px 15px rgba(0, 0, 0, .5)'
        self.css['div.window'] = {}
        self.css['div.window']['opacity'] = '0.9'
        self.css['div.window']['display'] = 'none'
        self.css['div.window']['position'] = 'absolute'
        self.css['div.window']['top'] = '45px'
        self.css['div.window']['left'] = '10%'
        self.css['div.window']['right'] = '10%'
        self.css['div.window']['margin'] = 'auto'
        self.css['div.window']['width'] = '80%'
        self.css['div.window']['height'] = 'auto'
        self.css['div.window']['background-color'] = '#FFFFFF'
        self.css['div.window']['z-index'] = '1055'
        self.css['div.window']['overflow'] = 'auto'
        self.css['div.window']['border'] = '0px solid rgba(0, 0, 0, .2)'
        self.css['div.window']['border-radius'] = '6px'
        self.css['div.window']['box-shadow'] = '0 5px 15px rgba(0, 0, 0, .5)'
        self.css['div.loading'] = {}
        self.css['div.loading']['display'] = 'none'
        self.css['div.loading']['overflow'] = 'hidden'
        self.css['div.loading']['position'] = 'fixed'
        self.css['div.loading']['z-index'] = '5000'
        self.css['div.loading']['top'] = '50px;'
        self.css['div.loading']['left'] = '0'
        self.css['div.loading']['height'] = '100%'
        self.css['div.loading']['width'] = '100%'
        self.css['div.loading']['background'] = 'rgba( 255, 255, 255, .8 )'
        self.css['div.loading']['background'] += "url(\'%s" % (images,)
        self.css['div.loading']['background'] += '/loader.gif\')'
        self.css['div.loading']['background'] += '50% 50% no-repeat'
        self.css['@media (min-width: 1350px)'] = {}
        self.css['@media (min-width: 1350px)']['.container'] = {}
        self.css['@media (min-width: 1350px)']['.container']['width'] = '1300px'
        self.css['@media (max-width: 1000px)'] = {}
        self.css['@media (max-width: 1000px)']['.navbar-header'] = {}
        self.css['@media (max-width: 1000px)']['.navbar-header']['float'] = 'none'
        self.css['@media (max-width: 1000px)']['.navbar-left,.navbar-right'] = {}
        self.css['@media (max-width: 1000px)']['.navbar-left,.navbar-right']['float'] = 'none !important'
        self.css['@media (max-width: 1000px)']['.navbar-toggle'] = {}
        self.css['@media (max-width: 1000px)']['.navbar-toggle']['display'] = 'block'
        self.css['@media (max-width: 1000px)']['.navbar-collapse'] = {}
        self.css['@media (max-width: 1000px)']['.navbar-collapse']['border-top'] = '1px solid transparent'
        self.css['@media (max-width: 1000px)']['.navbar-collapse']['box-shadow'] = 'inset 0 1px 0 rgba(255,255,255,0.1)'
        self.css['@media (max-width: 1000px)']['.navbar-fixed-top'] = {}
        self.css['@media (max-width: 1000px)']['.navbar-fixed-top']['top'] = '0'
        self.css['@media (max-width: 1000px)']['.navbar-fixed-top']['border-width'] = '0 0 1px'
        self.css['@media (max-width: 1000px)']['.navbar-collapse.collapse'] = {}
        self.css['@media (max-width: 1000px)']['.navbar-collapse.collapse']['display'] = 'none!important'
        self.css['@media (max-width: 1000px)']['.navbar-nav'] = {}
        self.css['@media (max-width: 1000px)']['.navbar-nav']['float'] = 'none!important'
        self.css['@media (max-width: 1000px)']['.navbar-nav']['margin-top'] = '7.5px'
        self.css['@media (max-width: 1000px)']['.navbar-nav>li'] = {}
        self.css['@media (max-width: 1000px)']['.navbar-nav>li']['float'] = 'none'
        self.css['@media (max-width: 1000px)']['.navbar-nav>li>a'] = {}
        self.css['@media (max-width: 1000px)']['.navbar-nav>li>a']['padding-top'] = '10px'
        self.css['@media (max-width: 1000px)']['.navbar-nav>li>a']['padding-bottom'] = '10px'
        self.css['@media (max-width: 1000px)']['.collapse.in'] = {}
        self.css['@media (max-width: 1000px)']['.collapse.in']['display'] = 'block !important'
        self.css['.dropdown-menu'] = {}
        self.css['.dropdown-menu']['border-radius'] = '0px'
        self.css['.dropdown-menu']['-webkit-box-shadow'] = 'none'
        self.css['.dropdown-menu']['box-shadow'] = 'none'
        self.css['.dropdown-submenu'] = {}
        self.css['.dropdown-submenu']['position'] = 'initial'
        self.css['.dropdown-submenu>.dropdown-menu'] = {}
        self.css['.dropdown-submenu>.dropdown-menu']['top'] = '0'
        self.css['.dropdown-submenu>.dropdown-menu']['left'] = '100%'
        self.css['.dropdown-submenu>.dropdown-menu']['margin-top'] = '-1px'
        self.css['.dropdown-submenu>.dropdown-menu']['margin-left'] = '-1px'
        self.css['.dropdown-submenu>.dropdown-menu']['-webkit-border-radius'] = '0'
        self.css['.dropdown-submenu>.dropdown-menu']['-moz-border-radius'] = '0'
        self.css['.dropdown-submenu>.dropdown-menu']['border-radius'] = '0'
        self.css['.dropdown-submenu>.dropdown-menu']['min-height'] = '101%'
        self.css['.dropdown-submenu:hover>.dropdown-menu'] = {}
        self.css['.dropdown-submenu:hover>.dropdown-menu']['display'] = 'block'
        self.css['.dropdown-submenu>a:after'] = {}
        self.css['.dropdown-submenu>a:after']['display'] = 'block'
        self.css['.dropdown-submenu>a:after']['content'] = '" "'
        self.css['.dropdown-submenu>a:after']['float'] = 'right'
        self.css['.dropdown-submenu>a:after']['width'] = '0'
        self.css['.dropdown-submenu>a:after']['height'] = '0'
        self.css['.dropdown-submenu>a:after']['border-color'] = 'transparent'
        self.css['.dropdown-submenu>a:after']['border-style'] = 'solid'
        self.css['.dropdown-submenu>a:after']['border-width'] = '5px 0 5px 5px'
        self.css['.dropdown-submenu>a:after']['border-left-color'] = '#ccc'
        self.css['.dropdown-submenu>a:after']['margin-top'] = '5px'
        self.css['.dropdown-submenu>a:after']['margin-right'] = '-10px'
        self.css['.dropdown-submenu:hover>a:after'] = {}
        self.css['.dropdown-submenu:hover>a:after']['border-left-color'] = '#fff'
        self.css['.dropdown-submenu.pull-left'] = {}
        self.css['.dropdown-submenu.pull-left']['float'] = 'none'
        self.css['.dropdown-submenu.pull-left>.dropdown-menu'] = {}
        self.css['.dropdown-submenu.pull-left>.dropdown-menu']['left'] = '-100%'
        self.css['.dropdown-submenu.pull-left>.dropdown-menu']['margin-left'] = '10px'
        self.css['.dropdown-submenu.pull-left>.dropdown-menu']['-webkit-border-radius'] = '6px 0 6px 6px'
        self.css['.dropdown-submenu.pull-left>.dropdown-menu']['-moz-border-radius'] = '6px 0 6px 6px'
        self.css['.dropdown-submenu.pull-left>.dropdown-menu']['border-radius'] = '6px 0 6px 6px'
        self.css['#popup'] = {}
        self.css['#popup']['z-index'] = '4000'
        self.css['#popup']['width'] = '300px'
        self.css['#popup']['position'] = 'fixed'
        self.css['#popup']['top'] = '50px'
        self.css['#popup']['left'] = 'auto'
        self.css['#popup']['right'] = '10px'
        self.css['#popup']['font-family'] = 'helvetica,arial,sans-serif'
        self.css['#popup']['font-size'] = '8pt'
        self.css['div.error'] = {}
        self.css['div.error']['background-color'] = '#f4e2e3'
        self.css['div.error']['color'] = '#9a6e6f'
        self.css['div.error']['display'] = 'none'
        self.css['div.warning'] = {}
        self.css['div.warning']['background-color'] = '#fff4c3'
        self.css['div.warning']['color'] = '#b09100'
        self.css['div.warning']['display'] = 'none'
        self.css['div.info'] = {}
        self.css['div.info']['background-color'] = '#deeff7'
        self.css['div.info']['color'] = '#6d8a98'
        self.css['div.info']['display'] = 'none'
        self.css['div.ids'] = {}
        self.css['div.ids']['color'] = '#006621'
        self.css['div.search_result'] = {}
        self.css['div.search_result']['padding-bottom'] = '10px'
        self.css['div.search_title'] = {}
        self.css['div.search_title']['color'] = ''
        self.css['div.search_title']['font-size'] = '18px'
        self.css['div.success'] = {}
        self.css['div.success']['background-color'] = '#e2f2dd'
        self.css['div.success']['color'] = '#598766'
        self.css['div.success']['display'] = 'none'
        self.css['div.popup'] = {}
        self.css['div.popup']['border-color'] = '#D8D8D8'
        self.css['div.popup']['border-style'] = 'solid'
        self.css['div.popup']['border-width'] = '1px'
        self.css['div.popup']['margin-bottom'] = '10px'
        self.css['div.popup']['margin-left'] = '0px'
        self.css['div.popup']['margin-right'] = '0px'
        self.css['div.popup']['margin-top'] = '0px'
        self.css['div.popup']['padding-bottom'] = '5px'
        self.css['div.popup']['padding-left'] = '5px'
        self.css['div.popup']['padding-right'] = '5px'
        self.css['div.popup']['padding-top'] = '5px'
        self.css['div.popup']['width'] = '100%'
        self.css['div.popup']['border-radius'] = '8px'
        self.css['div.popup']['overflow'] = 'hidden'
        self.css['div.signin'] = {}
        self.css['div.signin']['width'] = '50%'
        self.css['div.signin']['max-width'] = '400px'
        self.css['div.signin']['min-width'] = '200px'
        self.css['div.signin']['margin'] = 'auto'
        self.css['div.box'] = {}
        self.css['div.box']['width'] = 'auto'
        self.css['div.box']['border-style'] = 'solid'
        self.css['div.box']['padding-top'] = '2px'
        self.css['div.box']['padding-bottom'] = '2px'
        self.css['div.box']['padding-left'] = '2px'
        self.css['div.box']['padding-right'] = '2px'
        self.css['div.box']['border-color'] = '#e3e3e3'
        self.css['div.box']['background-color'] = '#f5f5f5'
        self.css['div.box']['border-width'] = '1px'
        self.css['div.box']['box-shadow'] = 'inset 0 1px 1px rgba(0,0,0,.05)'
        self.css['div.box']['border-radius'] = '3px'
        self.css['div.box']['margin-bottom'] = '5px'
        self.css['div.box']['font-family'] = 'helvetica,arial,sans-serif'
        self.css['div.box']['font-size'] = '12px'
        self.css['div.box']['min-height'] = '12px'
        self.css['div.block'] = {}
        self.css['div.block']['box-shadow'] = '5px 5px 5px #888888'
        self.css['div.block']['opacity'] = '0.8'
        self.css['div.block']['background-color'] = '#FFFFFF'
        self.css['div.block']['border-color'] = '#D8D8D8'
        self.css['div.block']['border-style'] = 'solid'
        self.css['div.block']['border-width'] = '1px'
        self.css['div.block']['color'] = '#5B5B5B'
        self.css['div.block']['font-family'] = 'helvetica,arial,sans-serif'
        self.css['div.block']['font-size'] = '12px'
        self.css['div.block']['margin-bottom'] = '10px'
        self.css['div.block']['margin-left'] = '0px'
        self.css['div.block']['margin-right'] = '0px'
        self.css['div.block']['margin-top'] = '0px'
        self.css['div.block']['padding-bottom'] = '5px'
        self.css['div.block']['padding-left'] = '5px'
        self.css['div.block']['padding-right'] = '5px'
        self.css['div.block']['padding-top'] = '5px'
        self.css['div.block']['width'] = '100%'
        self.css['div.block']['border-radius'] = '8px'
        self.css['span.title'] = {}
        self.css['span.title']['font-family'] = 'helvetica,arial,sans-serif'
        self.css['span.title']['font-weight'] = 'bold'
        self.css['div.block']['font-size'] = '12px'
        self.css['div.block_title'] = {}
        self.css['div.block_title']['border-bottom-width'] = '1px'
        self.css['div.block_title']['border-color'] = '#D8D8D8'
        self.css['div.block_title']['border-left-width'] = '0px'
        self.css['div.block_title']['border-right-width'] = '0px'
        self.css['div.block_title']['border-style'] = 'solid'
        self.css['div.block_title']['border-top-width'] = '0px'
        self.css['div.block_title']['color'] = '#318BBB'
        self.css['div.block_title']['font'] = "bold 15px 'lucida sans',"
        self.css['div.block_title']['font'] += "'trebuchet MS', 'Tahoma'"
        self.css['div.block_title']['margin-bottom'] = '5px'
        self.css['div.block_title']['margin-left'] = '0px'
        self.css['div.block_title']['margin-right'] = '0px'
        self.css['div.block_title']['margin-top'] = '0px'
        self.css['div.block_title']['width'] = '100%'
        self.css['div.block_content'] = {}
        self.css['div.block_content']['border-bottom-width'] = '0px'
        self.css['div.block_content']['border-left-width'] = '0px'
        self.css['div.block_content']['border-right-width'] = '0px'
        self.css['div.block_content']['border-top-width'] = '0px'
        self.css['div.block_content']['margin-bottom'] = '5px'
        self.css['div.block_content']['margin-left'] = '0px'
        self.css['div.block_content']['margin-right'] = '0px'
        self.css['div.block_content']['margin-top'] = '0px'
        self.css['div.block_content']['width'] = '100%'
        self.css['div.block_content']['overflow'] = 'hidden'
        self.css['div.block_menu'] = {}
        self.css['div.block_menu']['border-bottom-width'] = '0px'
        self.css['div.block_menu']['border-left-width'] = '0px'
        self.css['div.block_menu']['border-right-width'] = '0px'
        self.css['div.block_menu']['border-top-width'] = '0px'
        self.css['div.block_menu']['margin-bottom'] = '5px'
        self.css['div.block_menu']['margin-left'] = '0px'
        self.css['div.block_menu']['margin-right'] = '0px'
        self.css['div.block_menu']['margin-top'] = '0px'
        self.css['div.block_menu']['width'] = '100%'
        self.css['div.block_menu']['overflow'] = 'visible'
        self.css['div.menu'] = {}
        self.css['div.menu']['z-index'] = '1003'
        self.css['div.menu']['position'] = 'relative'
        self.css['div.menu_accounts'] = {}
        self.css['div.menu_accounts']['z-index'] = '1001'
        self.css['div.menu_accounts']['position'] = 'relative'
        self.css['div.menu_services'] = {}
        self.css['div.menu_services']['z-index'] = '1000'
        self.css['div.menu_services']['position'] = 'relative'
        self.css['div.push_top_searchbox'] = {}
        self.css['div.push_top_searchbox']['height'] = '40px'
        self.css['div.push_top_searchbox']['width'] = '100%'
        self.css['div.push_top_searchbox']['clear'] = 'both'
        self.css['div.push_top'] = {}
        self.css['div.push_top']['height'] = '70px'
        self.css['div.push_top']['width'] = '100%'
        self.css['div.push_top']['clear'] = 'both'
        self.css['div.push_top']['z-index'] = '1'
        self.css['div.push_bottom'] = {}
        self.css['div.push_bottom']['height'] = '25px'
        self.css['div.push_bottom']['width'] = '100%'
        self.css['div.push_bottom']['clear'] = 'both'
        self.css['div.push_bottom']['z-index'] = '1'
        self.css['.top-bar'] = {}
        self.css['.top-bar']['top'] = '50px'
        self.css['.top-bar']['padding-top'] = '50px'
        self.css['.top-bar']['padding-bottom'] = '5px'
        self.css['.top-bar']['margin-top'] = '0px'
        self.css['.top-bar']['margin-bottom'] = '5px'
        self.css['.top-bar']['width'] = '100%'
        self.css['.top-bar']['z-index'] = '1029'
        self.css['.tenant-bar-box'] = {}
        self.css['.tenant-bar-box']['padding-top'] = '8px'
        self.css['.tenant-bar-box']['padding-left'] = '8px'
        self.css['.tenant-bar-box']['padding-right'] = '8px'
        self.css['.tenant-bar-box']['padding-bottom'] = '8px'
        self.css['.tenant-bar-box']['border'] = '0px solid rgba(0, 0, 0, .2)'
        self.css['.tenant-bar-box']['border-radius'] = '0px 0px 6px 6px'
        self.css['.tenant-bar-box']['box-shadow'] = '0 5px 15px rgba(0, 0, 0, .5)'
        self.css['.search-bar-box'] = {}
        self.css['.search-bar-box']['padding-top'] = '8px'
        self.css['.search-bar-box']['padding-left'] = '8px'
        self.css['.search-bar-box']['padding-right'] = '8px'
        self.css['.search-bar-box']['padding-bottom'] = '8px'
        self.css['.search-bar-box']['border'] = '0px solid rgba(0, 0, 0, .2)'
        self.css['.search-bar-box']['border-radius'] = '0px 0px 6px 6px'
        self.css['.search-bar-box']['box-shadow'] = '0 5px 15px rgba(0, 0, 0, .5)'
        self.css['footer'] = {}
        self.css['footer']['background-color'] = '#5B5B5B'
        self.css['footer']['bottom'] = '0px'
        self.css['footer']['clear'] = 'both'
        self.css['footer']['color'] = '#FFFFFF'
        self.css['footer']['font-size'] = '12px'
        self.css['footer']['height'] = '20px'
        self.css['footer']['line-height'] = '20px'
        self.css['footer']['margin-bottom'] = '0px'
        self.css['footer']['margin-top'] = '0px'
        self.css['footer']['position'] = 'fixed'
        self.css['footer']['text-align'] = 'center'
        self.css['footer']['z-index'] = '1010'
        self.css['footer']['width'] = '100%'
        self.css['footer:before'] = {}
        self.css['footer:before']['content'] = "\"Tachyon Framework - Copyright (c) 2016 to 2017, Christiaan Frans Rademan, Allan Swanepoel, Dave Kruger. All rights resevered. BSD3-Clause License\""
        self.css['footer:after'] = {}
        self.css['.search-bar-box']['min-width'] = '40%'
        self.css['.tenant-bar-box']['min-width'] = '50%'

    def images(self, req, resp, image, theme_id=None):
        api = Client(req.context['restapi'])
        headers, response = api.execute(const.HTTP_GET, "/v1/theme/%s/images" % (theme_id,))
        if image.lower() == 'logo':
            img = response['logo']
            img_type = response['logo_type']
            img_name = response['logo_name']
            img_timestamp = response['logo_timestamp']

        if image.lower() == 'background':
            img = response['background']
            img_type = response['background_type']
            img_name = response['background_name']
            img_timestamp = response['background_timestamp']

        if image.lower() == 'background' or image.lower() == 'logo':
            if img is not None and img != '':
                img = base64.b64decode(img)
                resp.headers['content-type'] = img_type
                return img

    def themes(self, req, resp, theme_id=None):
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
        api = Client(req.context['restapi'])
        headers, response = api.execute(const.HTTP_DELETE, "/v1/theme/%s" % (theme_id,))
        self.view(req, resp)             

    def css_update(self, req, theme_id):
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
            css.append([ e, property[i], value[i] ])
            headers, response = api.execute(const.HTTP_PUT,
                                            url, obj=css)

    def images_update(self, req, theme_id):
        api = Client(req.context['restapi'])
        url = "/v1/images"
        url += "/%s" % (theme_id,)
        logo = req.post.getfile('logo')
        delete = req.query.get('delete_image')
        background = req.post.getfile('background')
        upload = {}
        if logo is not None:
            name, mtype, data = logo
            data = base64.b64encode(data)
            upload['logo'] = {}
            upload['logo']['name'] = name
            upload['logo']['type'] = mtype
            upload['logo']['data'] = data
        if background is not None:
            name, mtype, data = background
            data = base64.b64encode(data)
            upload['background'] = {}
            upload['background']['name'] = name
            upload['background']['type'] = mtype
            upload['background']['data'] = data
        if logo is not None or background is not None:
            headers, response = api.execute(const.HTTP_PUT,
                                            url, obj=upload)
        if delete is not None:
            if delete == 'logo':
                url += "/logo"
            elif delete == "background":
                url += "/background"
            headers, response = api.execute(const.HTTP_DELETE,
                                            url)

    def edit(self, req, resp, theme_id=None):
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
            element = select(req, 'element',source='tags')
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
        resp.headers['Content-Type'] = const.TEXT_CSS

        sheet = deepcopy(self.css)

        try:
            api = Client(req.context['restapi'])
            headers, custom = api.execute(const.HTTP_GET, "/v1/theme/%s/css" %
                                          (req.get_host(),))
            headers, images = api.execute(const.HTTP_GET, "/v1/theme/%s/images" %
                                          (req.get_host(),))
            if req.context['custom_background'] is True:
                sheet['body']['background-image'] = "url(\"%s/image/%s/background\")" % (req.app, req.get_host())

            for element in custom:
                if element not in sheet:
                    sheet[element] = {}
                for property in custom[element]:
                    sheet[element][property] = custom[element][property]
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
                    css(d[v], tab+1)
                    resp.write("%s}\n\n" % (spacer,))
                else:
                    val = "%s;" % (d[v].rstrip(';'),)
                    resp.write("%s%s: %s\n" % (spacer, v, val))

        css(sheet)

