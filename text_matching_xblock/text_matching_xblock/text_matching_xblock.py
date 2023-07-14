"""TO-DO: Write a description of what this XBlock is."""
import dataclasses
import uuid
from collections import defaultdict
from copy import copy

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Dict, List, ScopeIds, Float, Boolean

from text_matching_xblock.utils import render_template, generate_random_id
from xblock.scorable import ScorableXBlockMixin, Score
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblock.exceptions import JsonHandlerError


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


class TextMatchingXBlock(
    XBlock,
    ScorableXBlockMixin,
    StudioEditableXBlockMixin,
):
    """
    TO-DO: document what your XBlock does.
    """
    display_name = String(
        display_name="Title",
        help="The title of the drag and drop problem. The title is displayed to learners.",
        scope=Scope.settings,
        default="Text Matching Xblock",
        enforce_type=True,
    )

    description = String(
        display_name="Question",
        help="The description of the problem",
        scope=Scope.settings,
        default="",
        enforce_type=True,
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
                "text": "OptionffffOptionffffOptionffffOptionffff",
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
        scope=Scope.settings,
    )

    correct_answer = Dict(
        default={
            '1': '1',
            '2': '2',
            '3': '3'
        },
        scope=Scope.settings,
        help="Correct answer for score evaluation"
    )

    student_choices = Dict(
        default={},
        scope=Scope.user_state,
        help="A mapping from prompt_id to option_id that has been matched so far."
    )

    _has_submitted_answer = Boolean(
        help="Indicates whether a learner has completed the problem at least once",
        scope=Scope.user_state,
        default=False,
        enforce_type=True,
    )

    weight = Float(
        display_name="Problem Weight",
        help="Defines the number of points the problem is worth.",
        scope=Scope.settings,
        default=1,
        enforce_type=True,
    )

    _raw_earned = Float(
        help="Keeps maximum score achieved by student as a raw value",
        scope=Scope.user_state,
        default=0,
        enforce_type=True,
    )

    max_attempts = Integer(
        display_name="Maximum attempts",
        help="Defines the number of times a student can try to answer this problem. "
             "If the value is -1, infinite attempts are allowed.",
        scope=Scope.settings,
        default=-1,
        enforce_type=True,
    )

    attempts_used = Integer(
        display_name="Attempts learner has used so far",
        help="",
        scope=Scope.user_state,
        default=0,
        enforce_type=True,
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

        # For usage_id, "." change CSS Selectors, so it needs to be replaced too.
        # _id = _id.replace("+", "")
        # _id = _id.replace(":", "")
        # _id = _id.replace(".", "")

        # TODO: Replace this mock id with real random id
        _id = "randomidaiudbquwbc"

        return _id

    def student_view(self, context=None):
        """
        The primary view of the TextMatchingXBlock, shown to students
        when viewing courses.
        """
        frag = Fragment()

        js_urls = [
            "static/js/src/text_matching_xblock.js",
        ]
        for js_url in js_urls:
            frag.add_javascript(self.resource_string(js_url))
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.5.0/semantic.min.js")
        score = self.get_score()
        frag.initialize_js(
            'TextMatchingXBlock',
            {
                'xblock_id': self._get_xblock_unique_id(),
                'responses': self.options,
                'learner_choice': self.student_choices,
                'max_attempts': self.max_attempts,
                'is_graded': self.is_graded(),
                "has_submitted_answer": self.has_submitted_answer(),
                "weight_score_earned": score.raw_earned * self.weight,
                "weight_score_possible": score.raw_possible * self.weight,
            }
        )

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
        frag.add_css_url("//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.5.0/semantic.min.css")

        # Do not understand why 'add_javascript_url' default put script in body
        # instead of head, but to solve this issue, explicitly call 'add_resource_url'
        # to specify where to put this resource script.
        # frag.add_resource_url(
        #     url="https://cdn.jsdelivr.net/npm/@shopify/draggable@1.0.0-beta.11/lib/draggable.bundle.js",
        #     mimetype='application/javascript',
        #     placement='head',
        # )

        return frag

    def studio_view(self, context=None):
        frag = Fragment()

        js_urls = [
            "static/js/src/text_matching_studio.js",
        ]
        for js_url in js_urls:
            frag.add_javascript(self.resource_string(js_url))
        frag.initialize_js('TextMatchingStudioXBlock', {
            'settings': {
                "display_name": self.display_name,
                "description": self.description,
                "matching_items": [
                    {
                        "prompt": self.prompts[prompt_id]["text"],
                        "response": self.options[option_id]["text"]
                    }
                    for prompt_id, option_id in self.correct_answer.items()
                ],
                "weight": self.weight,
            }
        })

        html = render_template(
            template_name="text_matching_studio.html",
            context={
                "display_name": self._prepare_field_context("display_name"),
                "description": self._prepare_field_context("description"),
                "matching_items": [
                    {
                        "prompt": self.prompts[prompt_id],
                        "response": self.options[option_id]
                    }
                    for prompt_id, option_id in self.correct_answer.items()
                ],
                "weight": self._prepare_field_context("weight"),
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
        frag.add_css_url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css")

        return frag

    def _prepare_field_context(self, field_name: str):
        return self._make_field_info(field_name, self.fields[field_name])

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
            # Block content
            "display_name": self.display_name,
            "question": "Some dummy question",
            "id": self._get_xblock_unique_id(),
            # Problem content and learner attempt
            "matching_items": [
                {
                    "prompt": self.prompts[prompt_id],
                    "response": self.options[option_id],
                }
                for prompt_id, option_id in self.correct_answer.items()
            ],
            # Attempt result
            "attempts_used": self.attempts_used,
            "max_attempts": self.max_attempts,
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
            student_choice[first_option_id], student_choice[second_option_id] = student_choice[second_option_id], \
                student_choice[first_option_id]

        return {"result": "success"}

    @XBlock.json_handler
    def submit(self, data, suffix=''):
        """
        Handle learner submission and calculate the score
        """
        print("Learner submit")
        print(data)

        # Mark learner has submitted at least once
        self._has_submitted_answer = True
        if not self.max_attempts == -1 and self.attempts_used == self.max_attempts:
            raise JsonHandlerError(
                400,
                "You have run out of possible attempts",
            )
        self.attempts_used = self.attempts_used + 1

        # Evaluate submission and save score
        self.set_score(self.calculate_score())

        self._publish_grade(self.get_score())

        score = self.get_score()
        if score.raw_earned == score.raw_possible:
            result = "correct"
        elif score.raw_earned == 0:
            result = "incorrect"
        else:
            result = "partially_correct"

        return {
            "result": result,
            "weight_score_earned": score.raw_earned * self.weight,
            "weight_score_possible": score.raw_possible * self.weight,
            "attempts_used": self.attempts_used,
        }

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        print("Editor has update setting.")
        print(data)
        # TODO: Validate data
        if "display_name" in data:
            self.display_name = data["display_name"]
        if "description" in data:
            self.description = data["description"]
        if "weight" in data:
            self.weight = data['weight']
        if "matching_items" in data:
            self.update_matching_items(data["matching_items"])
        return {}

    def update_matching_items(self, items):
        """
        Update prompt, response and correct answer
        """
        _prompts = {}
        _responses = {}
        _answer = {}

        for item in items:
            prompt_id = generate_random_id()
            _prompts[prompt_id] = {
                "text": item["prompt"],
                "id": prompt_id,
            }

            response_id = generate_random_id()
            _responses[response_id] = {
                "text": item["response"],
                "id": response_id
            }

            _answer[prompt_id] = response_id

        self.prompts, self.options, self.correct_answer = (_prompts, _responses, _answer)

    @XBlock.json_handler
    def save_choice(self, data, suffix=''):
        # TODO: Validate data later, for now we will trust FE
        self.student_choices = data["learner_choice"]
        return {}

    @XBlock.json_handler
    def get_matching_item_template(self, data, suffix=''):
        """
        Endpoint for AJAX to get matching item template
        """
        response = {
            "template": render_template(
                "matching_item.html",
                context={},
            )
        }

        print(response)
        return response

    def has_submitted_answer(self) -> bool:
        return self._has_submitted_answer

    def max_score(self):
        return 1

    def get_score(self) -> Score:
        """
        Return the problem's current score as raw values.
        """
        return Score(
            raw_earned=self._raw_earned,
            raw_possible=self.max_score(),
        )

    def set_score(self, score: Score):
        self._raw_earned = score.raw_earned

    def calculate_score(self):
        correct_count = 0
        total_count = len(list(self.prompts.keys()))
        for prompt_id, option_id in self.student_choices.items():
            if option_id == self.correct_answer[prompt_id]:
                correct_count += 1

        # For now if all prompts are not matched correctly, learner score will be 0
        raw_score = self.max_score() if correct_count == total_count else 0
        print(f"Raw score earned {raw_score}")

        return Score(
            raw_earned=raw_score,
            raw_possible=self.max_score(),
        )

    def is_graded(self) -> bool:
        return getattr(self, "graded", False)

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
