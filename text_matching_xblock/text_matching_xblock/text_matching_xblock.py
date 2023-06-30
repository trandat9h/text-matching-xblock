"""TO-DO: Write a description of what this XBlock is."""
import dataclasses
import uuid
from collections import defaultdict

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Dict, List, ScopeIds

from text_matching_xblock.utils import render_template


@dataclasses.dataclass
class Dropzone:
    id: int


@dataclasses.dataclass
class OccupiedDropzone(Dropzone):
    text: str
    status: str = "occupied"


@dataclasses.dataclass
class BlankDropzone(Dropzone):
    status: str = "blank"


@dataclasses.dataclass
class HollowDropzone(Dropzone):
    text: str
    status: str = "hollow"


class TextMatchingXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """
    question = String(
        scope=Scope.content,
    )

    prompts = Dict(
        default={
            "1": {
                "text": "Prompt 1",
                "id": "1",
            },
            "2": {
                "text": "Prompt 2",
                "id": "2",
            },
            "3": {
                "text": "Prompt 3",
                "id": "3",
            },
        },
        scope=Scope.content,
    )

    options = Dict(
        default={
            "1": {
                "text": "Option 1",
                "id": "1",
            },
            "2": {
                "text": "Option 2",
                "id": "2",
            },
            "3": {
                "text": "Option 3",
                "id": "3",
            },
        },
        scope=Scope.content,
    )

    student_choices = Dict(
        default={},
        scope=Scope.user_state,
        help="A mapping from prompt_id to option_id that has been matched so far."
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def _get_xblock_unique_id(self) -> str:
        """
        Return unique ID of this block. Useful for HTML ID attributes.
        Works both in LMS/Studio and workbench runtimes:
        - In LMS/Studio, use the location.html_id method.
        - In the workbench, use the usage_id.
        """
        # TODO: Comment this below 3 lines since it needs further investigation for its unique
        # if hasattr(self, 'location'):
        #     _id = self.location.html_id()
        # else:
        _id = self.scope_ids.usage_id

        # This is a hacky way to make block id a valid CSS Selectors
        # With html_id, "+" and ":" is not a valid CSS Selectors
        _id = _id.replace("+", "").replace(":", "")

        # For usage_id, "." change CSS Selectors, so it needs to be replaced too.
        _id = _id.replace(".", "")

        return _id

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the TextMatchingXBlock, shown to students
        when viewing courses.
        """
        frag = Fragment()

        html = render_template(
            template_name="text_matching_xblock.html",
            context=self.prepare_matching_zone_template_context(),
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
        print(self._get_xblock_unique_id())
        frag.initialize_js(
            'TextMatchingXBlock',
            {
                "xblock_id": self._get_xblock_unique_id(),
            },
        )

        return frag

    def prepare_matching_zone_template_context(self) -> dict:
        prompt_context = list(self.prompts.values())

        # Prepare answer context
        answer_context = []
        for prompt_id, prompt in self.prompts.items():
            if option_id := self.student_choices.get(prompt_id):
                answer_context.append({
                    "status": "dropzone-occupied",
                    "id": prompt_id,
                    "text": self.options[option_id]["text"],
                })
            else:
                answer_context.append({
                    "status": "blank",
                    "id": prompt_id,
                })

        # Prepare option context
        chosen_option_ids = list(self.student_choices.values())
        option_context = [
            {
                "status": "hollow",
                "text": option["text"],
                "id": option["id"],
            }
            if option["id"] in chosen_option_ids
            else
            {
                "status": "origin-occupied",
                "text": option["text"],
                "id": option["id"],
            }
            for option in self.options.values()
        ]

        print(answer_context)
        return {
            "question": "Some dummy question",
            # TODO: Replace this dummy id will Xblock id for unique. This is IMPORTANT
            #  since multiple Matching Xblock can be used in one page.
            "id": self._get_xblock_unique_id(),
            "prompts": prompt_context,
            "answers": answer_context,
            "options": option_context,
        }

    @XBlock.json_handler
    def match_option(self, data, suffix=''):
        """
        Match/unmatch an option to an answer
        """
        print("match option")
        print(data)
        # TODO: Validate request here
        option_id = data["option_id"]
        answer_id = data["answer_id"]
        if not option_id:
            # Student remove an option

            # Remove option from student choice
            if not self.student_choices.get(answer_id):
                raise Exception()

            del self.student_choices[answer_id]
        else:
            # Student match an option to an answer
            if self.student_choices.get(answer_id):
                # Can not match an option to occupied answer
                raise Exception()

            self.student_choices[answer_id] = option_id

        return {"result": "success"}

    @XBlock.json_handler
    def swap_options(self, data, suffix=''):
        """
        Swap 2 options. This method also includes re-match the option to another blank answer
        """
        print("Swap option")
        print(data)
        # TODO: Validate request here
        student_choice = self.student_choices
        first_option_id = data["first_option_id"]
        second_option_id = data["second_option_id"]

        if not student_choice.get(first_option_id) and not student_choice.get(second_option_id):
            raise Exception()

        # If one of 2 options is chosen, remove the chosen one and assign that value to the remaining
        if answer := student_choice.get(first_option_id):
            student_choice[second_option_id] = answer
            del student_choice[first_option_id]

        elif answer := student_choice.get(second_option_id):
            student_choice[first_option_id] = answer
            del student_choice[second_option_id]

        # If 2 options are chosen, swap those
        else:
            # Swap 2 options
            student_choice[first_option_id], student_choice[second_option_id] = student_choice[second_option_id], student_choice[first_option_id]

        return {"result": "success"}

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
