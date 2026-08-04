# Internal capability routing

PPT Studio is autonomous. Use only its own workflow, scripts, references, and runtime. Never require or copy an external presentation skill.

## Default route

Use `assets/runtime/base-deck.html` as the starting runtime for self-contained HTML. Replace the sample content and extend its token system instead of replacing its navigation, editing, saving, theme, or accessibility contracts.

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
- PPTX: generate only when requested; report fidelity differences from HTML.
- Generated illustrations: use only after explicit approval.
- Authentication: explain the difference between a client-side gate and authenticated hosting.

## Coordinate contract

The HTML route uses a 1920 x 1080 stage. If another export library uses a different internal coordinate system, convert at the export boundary. Never mix coordinate systems inside the authored deck.
