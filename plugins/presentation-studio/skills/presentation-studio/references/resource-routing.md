# Internal capability routing

Presentation Studio is autonomous. Use only its own workflow, scripts, references, and runtime. Never require or copy an external presentation skill.

## Default route

Use `assets/runtime/base-deck.html` as the starting runtime for self-contained HTML. Copy it before authoring the full deck; replace its sample slides and extend its token system instead of replacing its navigation, editing, saving, theme, or accessibility contracts. Preserve the `presentation-studio-runtime` metadata, `data-presentation-studio-runtime="base-deck-v2"`, unified `deck-chrome`, audience/author split, edit baselines, core control IDs, dialogs, attribution block, and runtime script. A deck that recreates look-alike controls with a separate script is not a Presentation Studio runtime.

For structural revisions, keep a deterministic generator under `.work/`, write its candidate to a temporary file, and merge with `scripts/preserve_edits.py`. Never have the generator write directly over the user's current saved deck.

## Content and narrative

- Use `conversation-flow.md` for the interview sequence.
- Use `voice-and-story.md` before drafting titles.
- Use `expert-research.md` when subject-matter reasoning is needed.
- Use `content-planning.md` for slide contracts and evidence.

## Visual direction

- Use `visual-exploration.md` to make two or three comparable microdeck directions.
- Derive each direction from the approved brand, audience, venue, and content shape.
- Create original layouts from the 12-column stage grid and semantic design tokens.
- Do not imitate a named deck, template, designer, or repository closely enough to substitute for the original.

## Runtime and interaction

- Use `runtime-features.md` for navigation, editing, saving, notes, and exports.
- Use `theme-system.md` for light, dark, and custom themes.
- Use `motion-workflow.md` after the static design is stable.
- Use `host-compatibility.md` to adapt execution to available tools without changing the deliverable contract.

## Optional routes

- Presenter view: add only after approval and keep it isolated from the audience window.
- Hosted site: evaluate with `delivery-routing.md`; use only after approval and keep hosting concerns outside the deck runtime.
- Native PPTX or Google Slides: evaluate with `delivery-routing.md`; generate as a separate derivative and report fidelity differences from HTML.
- Generated illustrations: use only after explicit approval.
- Authentication: explain the difference between a client-side gate and authenticated hosting.

## Coordinate contract

The HTML route uses a 1920 x 1080 stage. If another export library uses a different internal coordinate system, convert at the export boundary. Never mix coordinate systems inside the authored deck.
