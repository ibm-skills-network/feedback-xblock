"""This XBlock configures a link to where an iframe for a feedback form is shown."""

from importlib.resources import files

from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Scope


class FeedbackXBlock(XBlock):
    """
    Allow configuration of a URL that will be put into an Iframe to allow students to give feedback
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    display_name = String(
        display_name='Name',
        default='Feedback form',
        scope=Scope.settings,
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        return files(__package__).joinpath(path).read_text(encoding="utf8")


    def student_view(self, context=None):
        """
        The primary view of the FeedbackXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/feedback.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/feedback.css"))
        frag.add_javascript(self.resource_string("static/js/src/feedback.js"))
        # The LMS looks this name up on window and calls it with (runtime, element). It has
        # to match the function name in feedback.js.
        frag.initialize_js('FeedbackXBlock')
        return frag

    def author_view(self, context=None):
        """
        The Studio view: the empty block with its CSS and no JS, so Studio shows no iframe.

        It must not call initialize_js. Studio would look up window.FeedbackXBlock, find
        nothing because the JS was never loaded, and throw a TypeError in the unit page.
        """
        html = self.resource_string("static/html/feedback.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/feedback.css"))
        return frag

    @XBlock.json_handler
    def get_course_id(self):
        try:
            return str(self.course_id)
        except Exception as err:
            return {
                "error": True,
                "message": "An error has occurred. Please refresh the page and try again. If this issue persists, contact support."
            }


    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("FeedbackXBlock",
             """<feedback/>
             """),
            ("Multiple FeedbackXBlock",
             """<vertical_demo>
                <feedback/>
                <feedback/>
                <feedback/>
                </vertical_demo>
             """),
        ]
