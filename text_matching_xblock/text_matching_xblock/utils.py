import os
from html import unescape as html_unescape
from typing import Optional, List, Any

from django.template import Context, Engine


def render_template(
    template_name: str,
    context: Optional[dict] = None,
):
    """
    Render static resource using provided context.

    Returns: django.utils.safestring.SafeText
    """
    if not context:
        context = {}

    # TODO: Line 13 - Find a generic to traverse all html files under static folder

    root_dir = os.path.dirname(__file__)
    template_dirs = [
        os.path.join(root_dir, 'static/html'),
        os.path.join(root_dir, 'templates/matching')
    ]

    # TODO: What if there are multiple template name matched?
    libraries = {'i18n': 'django.templatetags.i18n'}
    engine = Engine(dirs=template_dirs, debug=True, libraries=libraries)
    html = engine.get_template(template_name)

    return html_unescape(
        html.render(Context(context))
    )

