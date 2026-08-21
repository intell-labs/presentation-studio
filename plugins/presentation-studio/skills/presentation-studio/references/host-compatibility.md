# Host compatibility

The workflow and deliverable contract are host-independent. Adapt execution to capabilities, not product names.

## Capability check

At the start of production determine whether the host can:

- read and write local files;
- execute Python or JavaScript;
- browse official sources;
- inspect images and documents;
- run a local server;
- render or screenshot HTML.
- run DOM geometry checks or provide an equivalent browser automation surface.
- inspect a complete screenshot gallery with vision.
- publish a static site or equivalent hosted artifact;
- create or edit a native presentation file.

If a capability is unavailable, preserve the workflow and explain the smallest manual handoff. Do not omit approval gates silently.

Read `delivery-routing.md` when either optional delivery capability is relevant. Detect the capability by outcome rather than assuming product parity across hosts. Never install, connect, authenticate, or publish through an optional provider without explicit approval.

Rendered QA is capability-based:

- When Node and Playwright are available, run `scripts/qa_runtime.cjs` headlessly.
- When a host browser can inspect local HTTP previews, use it for the harmony review after deterministic QA passes.
- When direct browser control is unavailable, render screenshots headlessly and inspect the artifacts with the host's image-vision capability.
- Never claim visual completion from static HTML validation alone.
- A raw `file://` URL may be blocked by an interactive browser. Use the host-approved local preview mechanism when allowed; do not weaken or skip the headless gate.

## Distribution surfaces

- ChatGPT and Codex load `presentation-studio` from the OpenAI plugin package.
- Claude Code loads the same skill from the Claude plugin package.
- Claude Chat receives a release ZIP whose root folder is `presentation-studio/`.

The skill folder must not reference files outside itself. All Python utilities use the standard library so the package works in restricted execution environments.

## Invocation differences

Do not hardcode a slash command in the workflow. Users may invoke the skill explicitly or the host may select it from its description. Once loaded, present the same four-stage orientation and ask the same first question.

## Preview behavior

Never open a browser window automatically. When local preview is possible, start a server only when needed and provide the URL. When it is not possible, deliver the self-contained HTML and validation report.
