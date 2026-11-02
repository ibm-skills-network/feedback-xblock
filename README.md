# feedback-xblock

An [XBlock](https://docs.openedx.org/projects/xblock/) for Open edX. A course author adds
a "Feedback form" component to a unit. Learners then see the portal's course feedback
form inside an iframe in that unit.

## How it works

- `feedback/feedback.py` defines `FeedbackXBlock`. It has one field, `display_name`. Its
  `student_view` renders an empty `<div class="feedback_block">` and loads the CSS and JS
  from `feedback/static/`. Its `author_view` (Studio) renders the same div and CSS, but no
  JS, so Studio shows no iframe.
- `feedback/static/js/src/feedback.js` runs in the learner's browser. It reads the course
  id from the page (`data-course-id` in the LMS, `data-course-key` in Studio), strips the
  `courses.` or `studio.` prefix off the hostname, and adds an iframe pointing at
  `https://<portal host>/courses/<course id>/feedback/new?embed=true`. That page is served
  by the portal, not by this repo.
- `setup.py` registers the block under the `xblock.v1` entry point as `feedback`. That is
  the tag name course XML uses (`<feedback/>`), and how Open edX finds the class.

## Where it runs

The production Open edX image (`ibm-skills-network/tutor-config-vanilla`) has this repo as
a git submodule and runs `pip install -e` on it, on top of edx-platform's own pinned
requirements. Shipping a change means merging here, then moving that submodule to the new
commit and rebuilding the image.

The image currently runs Open edX Redwood on Python 3.11, so the XBlock, Django, lxml and
WebOb versions come from edx-platform, not from this repo. The image never reads
`requirements.txt`. Mend's dependency scan does, and Mend's bot edits it to fix reported
CVEs. CI tests against it too (see below).

## Tests

CI (`.github/workflows/tests.yml`) runs on every pull request:

- **python (redwood)**: pytest against the versions production runs, pinned in
  `requirements/redwood-constraints.txt`. Update that file when the image moves to a new
  Open edX release.
- **python (requirements.txt)**: pytest against `requirements.txt` with the newest versions
  it allows. A Mend bot PR that breaks the block fails here.
- **js**: `feedback.js` under Node's built-in test runner, with a stubbed DOM and jQuery.
  It has no npm dependencies.
- **tests**: passes only when all of the above pass. This is the check branch protection
  requires.

Run them locally:

```bash
python3.11 -m venv .venv
.venv/bin/pip install -c requirements/redwood-constraints.txt setuptools wheel
.venv/bin/pip install -c requirements/redwood-constraints.txt -e . -r requirements/test.txt
.venv/bin/python -m pytest

node --test tests/js/*.test.mjs
```
