# Presentation Studio by intell labs (part of intellbits.com)

Website: **https://intellbits.github.io/ppt-studio**

PPT Studio is an open-source presentation director developed by [intellbits](https://intellbits.com) for ChatGPT, Codex, Claude Code, and Claude Chat. It guides the user one question at a time through audience discovery, brand validation, speaker voice, subject-matter research, narrative, content approval, visual exploration, production, motion, and final QA.

The package exposes one canonical skill: `ppt-presentation-studio`. It is self-contained and does not require another presentation skill or framework.

## Product principles

- Ask one clear question at a time, with options and an example when useful.
- Inspect supplied resources before asking for information they already contain.
- Confirm structure and content before visual production.
- Compare a two- or three-slide microdeck before building the full deck.
- Match the presenter’s actual language instead of generic AI copy.
- Produce a fixed 16:9, self-contained HTML file by default.
- Deliver an audience-view default with one unified control cluster and an always-discoverable Author section whose actions explicitly enter author state.
- Include contextual per-element text and visual styling, safe save status, deep links, state-aware navigation, restrained motion, and light/dark/custom themes.
- Keep approved brand colors exact across themes; vary neutral surfaces and invert key-slide polarity instead of generating substitute shades.
- Preserve browser edits across generator revisions with stable IDs, baselines, and automatic backups.
- Validate every slide and progressive state after browser edits at desktop, laptop, phone portrait, and phone landscape sizes.
- Block delivery on rendered overlap, compressed or excessive text spacing, inconsistent connector geometry, overflow, orphan connectors, control/footer collisions, visually empty state-zero compositions, or excessive brand repetition.
- Validate visual-option galleries at all four target sizes, including initial loading, addressable option labels, 16:9 scaling, and responsive stacking.
- Require a human harmony review of final and initial states after deterministic geometry passes.

## Repository structure

```text
.agents/plugins/marketplace.json          OpenAI/Codex marketplace
.claude-plugin/marketplace.json           Claude Code marketplace
plugins/presentation-studio/
  .codex-plugin/plugin.json
  .claude-plugin/plugin.json
  skills/ppt-presentation-studio/
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

## Install for Codex

Register the repository as a marketplace and install `presentation-studio` from `ppt-studio-marketplace`, using `intellbits/ppt-studio` as the marketplace source. During local development, use the absolute repository path instead.

In Codex, invoke the installed skill explicitly as `$ppt-presentation-studio`. Codex may also select it automatically when the user asks for a presentation.

## Install for ChatGPT

Upload `ppt-presentation-studio-<version>-chatgpt.zip` from ChatGPT’s Skills area using Create → Upload from your computer. Skill availability and upload permissions depend on the user’s plan and workspace settings. After installation, ChatGPT may select the skill automatically when it is relevant.

## Install for Claude Code

```bash
claude plugin marketplace add intellbits/ppt-studio
claude plugin install presentation-studio@ppt-studio-marketplace
```

Invoke the skill explicitly in Claude Code as `/presentation-studio:ppt-presentation-studio`.

For local testing, replace `intellbits/ppt-studio` with the absolute repository path.

## Install for Claude Chat

Download `ppt-presentation-studio-<version>-claude.zip` from the [latest release](https://github.com/intellbits/ppt-studio/releases/latest) and upload it from Claude’s Customize → Skills interface. It appears as **Presentation Studio by intell labs (part of intellbits.com)**. The ZIP contains the skill folder at its root and needs no external repositories.

To build the same archive locally instead, run the packaging commands below; `dist/` is not tracked in the repository.

## Validate and package

```bash
python3 scripts/validate_all.py
python3 scripts/build_release.py
```

The build produces a Codex plugin ZIP, a ChatGPT skill ZIP, a Claude skill ZIP, and SHA-256 checksums in `dist/`. Share the two skill ZIPs with ChatGPT and Claude users; the Codex plugin ZIP is for marketplace distribution.

## Versioning

PPT Studio uses plain semantic versions in `MAJOR.MINOR.PATCH` form. Release and plugin manifests must carry the same value; date suffixes and build metadata are not used. Routine compatible improvements increment the patch version, for example `1.0.2` → `1.0.3`.

## Included presentation utilities

From `plugins/presentation-studio/skills/ppt-presentation-studio/`:

```bash
python3 scripts/init_project.py <output-directory>
python3 scripts/validate_project.py <output-directory>/presentation-project.json --phase delivery
python3 scripts/bundle_html.py presentation.html --strict
python3 scripts/validate_html.py presentation-self-contained.html --strict
python3 scripts/extract_visible_text.py presentation-self-contained.html --output final-text.txt
python3 scripts/preserve_edits.py presentation.html .work/presentation-generated.html --output presentation.html
python3 scripts/make_preview_gallery.py option-a.html option-b.html --output visual-options.html
node scripts/qa_runtime.cjs presentation.html --project presentation-project.json --output-dir work/visual-qa
node scripts/qa_gallery.cjs visual-options.html --output-dir work/gallery-qa
```

Generated decks include a contextual toolbar that opens beside the selected text or safe visual component. Text controls cover approved family, bounded size, color, emphasis, and alignment; visual controls cover fill, border, radius, shadow, and opacity. The complete typography dialog remains available for weight, line-height, tracking, and other precise adjustments. Rendered QA blocks delivery when the editor clips, escapes the viewport, or produces text outside readable semantic ranges.

## External projects reviewed

Several open-source presentation and design skills were reviewed as product references. No source code, template, runtime, asset, or instruction file from those projects is bundled in PPT Studio 1.0. See `THIRD_PARTY_NOTICES.md` and `release/vendor-lock.json`.

## License, attribution, and presentations

The source code is available under the Apache License 2.0. Keep the supplied `NOTICE` when redistributing the source or a derivative distribution. The runtime carries discreet generator metadata and an About panel; it does not place a permanent intellbits watermark on presentation slides.

Users retain the rights they hold in their own presentation content and assets. The embedded PPT Studio runtime remains Apache-2.0, and third-party assets remain subject to their respective terms.

The Apache license does not grant trademark rights. See `TRADEMARKS.md` for permitted references to intellbits and PPT Studio and for rules that prevent forks from implying official endorsement.

## Brand

Originally developed and maintained by [intellbits](https://intellbits.com).

Apache License 2.0. Copyright 2026 intellbits.
