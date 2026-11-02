// Runs feedback.js in a sandbox with a fake document and a fake jQuery. The stubs only
// cover the calls feedback.js makes. If it starts using more of jQuery or the DOM, these
// tests fail with a TypeError, and the stubs need to grow with it.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import vm from "node:vm";

const source = readFileSync(
  new URL("../../feedback/static/js/src/feedback.js", import.meta.url),
  "utf8",
);

function render({ protocol = "https:", host, attrs = {} }) {
  const container = { children: [], appendChild(el) { this.children.push(el); } };
  const elementWith = (name) => ({ getAttribute: (a) => (a === name ? attrs[name] : null) });
  const selectors = {
    ".feedback_block": [container],
    "[data-course-id]": "data-course-id" in attrs ? [elementWith("data-course-id")] : [],
    "[data-course-key]": "data-course-key" in attrs ? [elementWith("data-course-key")] : [],
  };
  const $ = (arg) => {
    if (typeof arg === "function") return arg(); // $(fn) runs fn on page load
    return { toArray: () => selectors[arg] };
  };
  const document = { location: { protocol, host }, createElement: (tag) => ({ tag }) };

  const sandbox = { $, document };
  vm.runInNewContext(source, sandbox);
  sandbox.FeedbackXBlock({}, {});
  return container.children;
}

test("LMS: iframe points at the feedback form for the course on the page", () => {
  const [frame] = render({
    host: "courses.example.skills.network",
    attrs: { "data-course-id": "course-v1:IBM+X101+2026" },
  });
  assert.equal(frame.tag, "iframe");
  assert.equal(
    frame.src,
    "https://example.skills.network/courses/course-v1:IBM+X101+2026/feedback/new?embed=true",
  );
  assert.equal(frame.title, "Feedback Form");
  assert.equal(frame.width, "100%");
  assert.equal(frame.height, "700rem");
});

test("Studio: course id comes from data-course-key", () => {
  const [frame] = render({
    host: "studio.example.skills.network",
    attrs: { "data-course-key": "course-v1:IBM+X101+2026" },
  });
  assert.equal(
    frame.src,
    "https://example.skills.network/courses/course-v1:IBM+X101+2026/feedback/new?embed=true",
  );
});

test("keeps the page's protocol", () => {
  const [frame] = render({
    protocol: "http:",
    host: "courses.localhost:8000",
    attrs: { "data-course-id": "c1" },
  });
  assert.equal(frame.src, "http://localhost:8000/courses/c1/feedback/new?embed=true");
});

test("any other host gets an empty course id", () => {
  const [frame] = render({ host: "example.skills.network" });
  assert.equal(frame.src, "https://example.skills.network/courses//feedback/new?embed=true");
});
