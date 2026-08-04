# PPT Studio by intellbits

Website: **https://intellbits.github.io/ppt-studio**

PPT Studio is an open-source presentation director developed by [intellbits](https://intellbits.com) for ChatGPT, Codex, Claude Code, and Claude Chat. It guides the user one question at a time through audience discovery, brand validation, speaker voice, subject-matter research, narrative, content approval, visual exploration, production, motion, and final QA.

The package exposes one canonical skill: `presentation-director`. It is self-contained and does not require another presentation skill or framework.

## Product principles

- Ask one clear question at a time, with options and an example when useful.
- Inspect supplied resources before asking for information they already contain.
- Confirm structure and content before visual production.
- Compare a two- or three-slide microdeck before building the full deck.
- Match the presenter’s actual language instead of generic AI copy.
- Produce a fixed 16:9, self-contained HTML file by default.
- Include text editing, save status, deep links, state-aware navigation, restrained motion, and light/dark/custom themes.
- Validate the final HTML after browser edits.

## Repository structure

```text
.agents/plugins/marketplace.json          OpenAI/Codex marketplace
.claude-plugin/marketplace.json           Claude Code marketplace
plugins/ppt-studio/
  .codex-plugin/plugin.json
  .claude-plugin/plugin.json
  skills/presentation-director/
    SKILL.md
    agents/openai.yaml
    assets/runtime/base-deck.html
    references/
    scripts/
release/
  manifest.json
  vendor-lock.json
scripts/
  build_release.py
  validate_all.py
tests/
```

## Install for Codex and ChatGPT

Register the repository as a marketplace and install `ppt-studio` from `ppt-studio-marketplace`, using `intellbits/ppt-studio` as the marketplace source. During local development, use the absolute repository path instead.

The installed skill can be invoked explicitly as `$presentation-director`, or selected automatically when the user asks for a presentation.

## Install for Claude Code

```bash
claude plugin marketplace add intellbits/ppt-studio
claude plugin install ppt-studio@ppt-studio-marketplace
```

For local testing, replace `intellbits/ppt-studio` with the absolute repository path.

## Install for Claude Chat

Download `presentation-director-<version>-claude.zip` from the [latest release](https://github.com/intellbits/ppt-studio/releases/latest) and upload it from Claude’s Customize → Skills interface. The ZIP contains the skill folder at its root and needs no external repositories.

To build the same archive locally instead, run the packaging commands below; `dist/` is not tracked in the repository.

## Validate and package

```bash
python3 scripts/validate_all.py
python3 scripts/build_release.py
```

The build produces a plugin ZIP, a Claude Chat skill ZIP, and SHA-256 checksums in `dist/`.

## Included presentation utilities

From `plugins/ppt-studio/skills/presentation-director/`:

```bash
python3 scripts/init_project.py <output-directory>
python3 scripts/validate_project.py <output-directory>/presentation-project.json --phase delivery
python3 scripts/bundle_html.py presentation.html --strict
python3 scripts/validate_html.py presentation-self-contained.html --strict
python3 scripts/extract_visible_text.py presentation-self-contained.html --output final-text.txt
```

## External projects reviewed

Several open-source presentation and design skills were reviewed as product references. No source code, template, runtime, asset, or instruction file from those projects is bundled in PPT Studio 1.0. See `THIRD_PARTY_NOTICES.md` and `release/vendor-lock.json`.

## License, attribution, and presentations

The source code is available under the Apache License 2.0. Keep the supplied `NOTICE` when redistributing the source or a derivative distribution. The runtime carries discreet generator metadata and an About panel; it does not place a permanent intellbits watermark on presentation slides.

Users retain the rights they hold in their own presentation content and assets. The embedded PPT Studio runtime remains Apache-2.0, and third-party assets remain subject to their respective terms.

The Apache license does not grant trademark rights. See `TRADEMARKS.md` for permitted references to intellbits and PPT Studio and for rules that prevent forks from implying official endorsement.

## Brand

Originally developed and maintained by [intellbits](https://intellbits.com).

Apache License 2.0. Copyright 2026 intellbits.
