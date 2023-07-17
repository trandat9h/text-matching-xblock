"""TO-DO: Write a description of what this XBlock is."""
import random
from typing import Optional

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Dict, Float, Boolean

from text_matching_xblock.enums import EvaluationMode
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
    has_score = True

    display_name = String(
        display_name="Title",
        help="The title of the problem. The title is displayed to learners.",
        scope=Scope.settings,
        default="Text Matching Xblock",
        enforce_type=True,
    )

    description = String(
        display_name="Description",
        help="The description of the problem",
        scope=Scope.settings,
        default="The description of the problem",
        enforce_type=True,
        multiline_editor=True
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

    responses = Dict(
        default={
            "1": {
                "text": "Response 1",
                "id": "1",
            },
            "2": {
                "text": "Response 2",
                "id": "2",
            },
            "3": {
                "text": "Response 3",
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

    evaluation_mode = String(
        display_name="Mode",
        help=(
            "Standard mode: the problem provides immediate feedback each time "
            "a learner drops an item on a target zone. "
            "Assessment mode: the problem provides feedback only after "
            "a learner drops all available items on target zones."
        ),
        scope=Scope.settings,
        values=[
            {"display_name": "Standard", "value": EvaluationMode.STANDARD},
            {"display_name": "Assessment", "value": EvaluationMode.ASSESSMENT},
        ],
        default=EvaluationMode.STANDARD,
        enforce_type=True,
    )

    _is_evaluation_mode_manually_edited = Boolean(
        display_name="Mode is manually edited",
        help="Whether editor has manually edit evaluation mode. If False the mode come from default section setting",
        scope=Scope.settings,
        default=False,
        enforce_type=True,
    )

    student_choices = Dict(
        default={},
        scope=Scope.user_state,
        help="A mapping from prompt_id to response_id that has been matched so far."
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
        default=1.0,
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
        default=3,
        enforce_type=True,
    )

    attempts_used = Integer(
        display_name="Attempt used",
        help="Attempts learner has used so far",
        scope=Scope.user_state,
        default=0,
        enforce_type=True,
    )

    show_reset_button = Boolean(
        display_name="Show Reset Button",
        help="Show Reset Button to allow learner to reset their choice",
        scope=Scope.settings,
        default=True,
        enforce_type=True,
    )

    show_save_button = Boolean(
        display_name="Show Save Button",
        help="Show Save Button to allow learner to save their choice so that they can come back later.",
        scope=Scope.settings,
        default=True,
        enforce_type=True,
    )

    show_answer_option = String(
        display_name="Show Answer Option",
        help="Whether Learner can see the correct answer or not",
        scope=Scope.settings,
        values=[
            {"display_name": "Always", "value": ShowAnswerOption.ALWAYS},
            {"display_name": "Never", "value": ShowAnswerOption.NEVER},
        ],
        default=ShowAnswerOption.ALWAYS,
        enforce_type=True,
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    @staticmethod
    def _get_xblock_unique_id() -> str:
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

        _id = f'textmatching-xblock-{generate_random_id()}'

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
                'responses': self.responses,
                'learner_choice': self.student_choices,
                'attempts_used': self.attempts_used,
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
                        "response": self.responses[response_id]["text"]
                    }
                    for prompt_id, response_id in self.correct_answer.items()
                ],
                "weight": self.weight,
                "evaluation_mode": {
                    "value": self.evaluation_mode,
                    "is_edited": self._is_evaluation_mode_manually_edited,
                }
            }
        })

        self.update_evaluation_mode(
            is_edited=self._is_evaluation_mode_manually_edited,
            eval_mode=self.evaluation_mode,
        )
        html = render_template(
            template_name="text_matching_studio.html",
            context={
                "display_name": self._prepare_field_context("display_name"),
                "description": self._prepare_field_context("description"),
                "matching_items": [
                    {
                        "prompt": self.prompts[prompt_id],
                        "response": self.responses[response_id]
                    }
                    for prompt_id, response_id in self.correct_answer.items()
                ],
                "weight": self._prepare_field_context("weight"),
                "evaluation_mode": self._prepare_field_context("evaluation_mode"),
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

    def get_student_view_context(self) -> dict:
        return {
            # Block content
            "display_name": self.display_name,
            "description": self.description,
            "id": self._get_xblock_unique_id(),
            # Problem content and learner attempt
            "matching_items": [
                {
                    "prompt": self.prompts[prompt_id],
                    "response": self.responses[response_id],
                }
                for prompt_id, response_id in self.correct_answer.items()
            ],
            "show_answer_button": self.can_show_answer(),
            "show_reset_button": self.show_reset_button,
            "show_save_button": self.show_save_button,
            # Attempt result
            "attempts_used": self.attempts_used,
            "max_attempts": self.max_attempts,
        }

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
        if "evaluation_mode" in data:
            self.update_evaluation_mode(
                eval_mode=data["evaluation_mode"]["value"],
                is_edited=data["evaluation_mode"]["is_edited"],
            )
        if "show_answer_option" in data:
            self.show_answer_option = data["show_answer_option"]
        if "show_save_button" in data:
            self.show_answer_option = data["show_save_button"]
        if "show_reset_button" in data:
            self.show_answer_option = data["show_reset_button"]
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

        self.prompts, self.responses, self.correct_answer = (_prompts, _responses, _answer)

    def update_evaluation_mode(
        self,
        is_edited: bool,
        eval_mode: Optional[str] = None,
    ):
        print(is_edited)
        print(eval_mode)
        self._is_evaluation_mode_manually_edited = is_edited

        if is_edited:
            # TODO: Validate evaluate_mode here
            self.evaluation_mode = eval_mode
            return

        # If Course editor does not modify this setting, get the value from 'graded' attribute
        if self.is_graded():
            self.evaluation_mode = EvaluationMode.ASSESSMENT
            return

        self.evaluation_mode = EvaluationMode.STANDARD

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
        return 1.0

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
        for prompt_id, response_id in self.student_choices.items():
            if response_id == self.correct_answer[prompt_id]:
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

    @XBlock.json_handler
    def show_answer(self, data, suffix=''):
        if not self.evaluation_mode == EvaluationMode.STANDARD:
            raise JsonHandlerError(
                403,
                "Can only receive answer in STANDARD mode"
            )

        if not self.can_show_answer():
            raise JsonHandlerError(
                403,
                "The problem is not allowed to show answer"
            )

        return {
            "answer": self.correct_answer
        }

    def can_show_answer(self) -> bool:
        """
        Determine whether the block can show answer to learner or not
        """
        is_shown = False
        if self.show_answer_option == ShowAnswerOption.ALWAYS:
            is_shown = True
        elif self.show_answer_option == ShowAnswerOption.NEVER:
            is_shown = False
        elif self.show_answer_option == ShowAnswerOption.AFTER_ATTEMPTED and self.attempts_used >= 1:
            is_shown = True

        # TODO: Implement after_some_after and past_due later
        return is_shown

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
