js = []
css = []


def render(req):
    """ Function render.

    Used by tachyonic.ui.middleware to populate jinja.globals['HTML_ASSETS'].

    Args:
        req (object): Request Object (tachyonic.neutrino.wsgi.request.Request).

    Returns:
        string containing html with <link> and <script> resources.
    """
    r = []

    for j in js:
        r.append("    <script src='%s/%s'></script>" % (req.get_app_static(), j))

    for c in css:
        r.append("    <link rel='stylesheet' href='%s/%s'/>" % (req.get_app_static(), c))

    return "\n".join(r)
