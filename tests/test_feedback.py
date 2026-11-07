import shutil
import subprocess
import sys
import zipfile
from importlib.metadata import entry_points
from pathlib import Path

from xblock.core import XBlock
from xblock.fields import Scope, ScopeIds
from xblock.runtime import DictKeyValueStore, KvsFieldData
from xblock.test.tools import TestRuntime

from feedback import FeedbackXBlock

REPO = Path(__file__).resolve().parent.parent

STATIC_FILES = [
    "feedback/static/html/feedback.html",
    "feedback/static/css/feedback.css",
    "feedback/static/js/src/feedback.js",
]


def make_runtime():
    return TestRuntime(services={"field-data": KvsFieldData(DictKeyValueStore())})


def make_block():
    runtime = make_runtime()
    return runtime.construct_xblock_from_class(
        FeedbackXBlock, ScopeIds("user", "feedback", "def_id", "usage_id")
    )


def test_entry_point_loads_the_block():
    # Open edX finds the block by the tag name in course XML ("feedback") through the
    # xblock.v1 entry point. If setup.py breaks this, every course using the block
    # shows an error in its place.
    (ep,) = [ep for ep in entry_points(group="xblock.v1") if ep.name == "feedback"]
    assert ep.load() is FeedbackXBlock
    assert XBlock.load_class("feedback") is FeedbackXBlock


def test_display_name_default_and_scope():
    block = make_block()
    assert block.display_name == "Feedback form"
    assert FeedbackXBlock.display_name.scope == Scope.settings


def test_student_view_ships_html_css_and_js():
    frag = make_block().student_view()

    # feedback.js puts the iframe in this div. Without it, learners see nothing.
    assert 'class="feedback_block"' in frag.content

    resources = sorted((r.kind, r.mimetype) for r in frag.resources)
    assert resources == [("text", "application/javascript"), ("text", "text/css")]
    js = next(r.data for r in frag.resources if r.mimetype == "application/javascript")
    assert "function FeedbackXBlock(runtime, element)" in js
    assert frag.js_init_fn == "FeedbackXBlock"


def test_author_view_ships_html_and_css_only():
    frag = make_block().author_view()
    assert 'class="feedback_block"' in frag.content
    assert [r.mimetype for r in frag.resources] == ["text/css"]
    assert frag.js_init_fn is None


def test_parses_from_course_xml_and_keeps_display_name():
    runtime = make_runtime()
    usage_id = runtime.parse_xml_string('<feedback display_name="Tell us more"/>')
    block = runtime.get_block(usage_id)
    assert isinstance(block, FeedbackXBlock)
    assert block.display_name == "Tell us more"


def test_wheel_contains_static_files(tmp_path):
    # Production uses an editable install, which reads the files from the checkout. A
    # normal install only gets what package_data in setup.py lists, so this checks that
    # list too. The build runs on a copy because setuptools reuses an existing build/
    # directory, and a stale one would still hold files that package_data dropped.
    src = tmp_path / "src"
    shutil.copytree(REPO / "feedback", src / "feedback",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(REPO / "setup.py", src)
    subprocess.run(
        [sys.executable, "-m", "pip", "wheel", str(src), "--no-deps", "--no-build-isolation",
         "-q", "-w", str(tmp_path / "dist")],
        check=True,
    )
    (wheel,) = (tmp_path / "dist").glob("*.whl")
    names = zipfile.ZipFile(wheel).namelist()
    for path in STATIC_FILES:
        assert path in names


def test_get_course_id_handler_answers_a_request():
    # Calls the handler through the runtime, the way the LMS does. A handler that does not
    # take (data, suffix) fails here with a TypeError.
    from webob import Request

    block = make_block()
    block.course_id = "course-v1:IBM+CL0101EN+v1"
    request = Request.blank("/", method="POST", body=b"{}")
    response = block.runtime.handle(block, "get_course_id", request)
    assert response.status_code == 200
    assert response.json == "course-v1:IBM+CL0101EN+v1"
