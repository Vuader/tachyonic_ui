from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from tachyonic.neutrino.web.bootstrap3.forms import Form as Bootstrap

from tachyonic.common.models import themes

log = logging.getLogger(__name__)


class Theme(Bootstrap, themes.Theme):
    pass

