from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from tachyonic.neutrino.web.bootstrap3.forms import Form as Bootstrap

from tachyonic.common.models import domains

log = logging.getLogger(__name__)

class Domain(Bootstrap, domains.Domain):
    pass
