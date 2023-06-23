"""TO-DO: Write a description of what this XBlock is."""
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope

from text_matching_xblock.utils import render_template

class TextMatchingXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    count = Integer(
        default=0, scope=Scope.user_state,
        help="A simple counter, to show something happening",
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the TextMatchingXBlock, shown to students
        when viewing courses.
        """
        frag = Fragment()

        html = render_template(
            template_name="text_matching_xblock.html",
            context={
                "question": "Some dummy question",
                # TODO: Replace this dummy id will Xblock id for unique. This is IMPORTANT
                #  since multiple Matching Xblock can be used in one page.
                "id": "UniqueDropzone",
                # TODO: Replace this dummy prompts by real prompt. Currently let's mock this by 3 prompts
                "prompts": [
                    "Prompt 1",
                    "Prompt 2",
                    "Prompt 3",
                ],
            },
        )
        frag.add_content(html)

        css_resources = (
            "static/css/text_matching_xblock.css",
            "static/css/matching/block.css",
            "static/css/matching/matching_zone.css"
        )
        for css_resource in css_resources:
            frag.add_css(self.resource_string(css_resource))

        # Do not understand why 'add_javascript_url' default put script in body
        # instead of head, but to solve this issue, explicitly call 'add_resource_url'
        # to specify where to put this resource script.
        frag.add_resource_url(
            url="https://cdn.jsdelivr.net/npm/@shopify/draggable@1.0.0-beta.11/lib/draggable.bundle.js",
            mimetype='application/javascript',
            placement='head',
        )

        frag.add_javascript(self.resource_string("static/js/src/text_matching_xblock.js"))
        frag.initialize_js('TextMatchingXBlock')

        frag.add_javascript(self.resource_string("static/js/src/drag_and_drop.js"))

        return frag

    # TO-DO: change this handler to perform your own actions.  You may need more
    # than one handler, or you may not need any handlers at all.
    @XBlock.json_handler
    def increment_count(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'

        self.count += 1
        return {"count": self.count}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("TextMatchingXBlock",
             """<text_matching_xblock/>
             """),
            ("Multiple TextMatchingXBlock",
             """<vertical_demo>
                <text_matching_xblock/>
                <text_matching_xblock/>
                <text_matching_xblock/>
                </vertical_demo>
             """),
        ]
