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

If a capability is unavailable, preserve the workflow and explain the smallest manual handoff. Do not omit approval gates silently.

## Distribution surfaces

- ChatGPT and Codex load `presentation-director` from the OpenAI plugin package.
- Claude Code loads the same skill from the Claude plugin package.
- Claude Chat receives a release ZIP whose root folder is `presentation-director/`.

The skill folder must not reference files outside itself. All Python utilities use the standard library so the package works in restricted execution environments.

## Invocation differences

Do not hardcode a slash command in the workflow. Users may invoke the skill explicitly or the host may select it from its description. Once loaded, present the same four-stage orientation and ask the same first question.

## Preview behavior

Never open a browser window automatically. When local preview is possible, start a server only when needed and provide the URL. When it is not possible, deliver the self-contained HTML and validation report.
