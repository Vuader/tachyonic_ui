import re

def get_form_value(name, text):
    match = re.search('<(?=.* id="%s")[^>]*value="([^"]+).*>' % (name,), text)
    if match is not None:
        return match.group(1)
    return None
