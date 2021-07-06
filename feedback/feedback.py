"""This XBlock configures a link to where an iframe for a feedback form is shown."""

import pkg_resources

from django.contrib.auth.models import User
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Scope


class FeedbackXBlock(XBlock):
    """
    Allow configuration of a URL that will be put into an Iframe to allow students to give feedback
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def student_view(self, context=None):
        """
        The primary view of the FeedbackXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/feedback.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/feedback.css"))
        frag.add_javascript(self.resource_string("static/js/src/feedback.js"))
        frag.initialize_js('FeedbackXBlock')
        return frag

    def author_view(self, context=None):
        html = self.resource_string("static/html/feedback.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/feedback.css"))
        frag.add_javascript(self.resource_string("static/js/src/feedback.js"))
        frag.initialize_js('FeedbackXBlock')
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
