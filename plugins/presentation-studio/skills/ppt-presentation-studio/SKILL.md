---
name: ppt-presentation-studio
description: Guide, research, plan, design, build, enhance, and validate professional presentations as self-contained HTML by default, with optional presenter tools, PDF, and PPTX. Use for new decks, pitch decks, financial or corporate presentations, reports, talks, training, product launches, converting source documents into slides, or improving an existing HTML/PPTX presentation. Use a one-question-at-a-time workflow, validate audience, brand, speaker voice, expert perspective, narrative, content, visual direction, motion, and final rendered text before delivery.
---

# PPT Presentation Studio

Create presentations through deliberate checkpoints. Prefer a portable, fixed-stage, self-contained HTML file. Do not require any other installed skill. Optional hosting or native-presentation capabilities may extend delivery only when they are available, useful, and approved by the user.

## Core operating rules

1. Start with this brief orientation:

   > Crearemos tu presentación en cuatro etapas: 1) entender objetivo, audiencia y recursos; 2) validar estructura, narrativa y contenido; 3) comparar estilos con un microdeck; 4) producir, revisar y entregar. Avanzaremos paso a paso y no diseñaré toda la presentación sin tu aprobación. Vamos con la primera pregunta.

2. Ask one question per turn. For any non-obvious question, provide concise options, one context-specific example, and a recommendation when appropriate.
3. Inspect supplied resources before asking questions they already answer.
4. Keep `presentation-project.json` as the source of truth. Update it after every confirmed decision.
5. Do not create full-deck visuals before structure, content, and voice are approved.
6. Do not generate illustrations unless the user explicitly requests them.
7. Avoid generic AI language. Match the speaker's real vocabulary, regional register, directness, and sentence rhythm.
8. Do not execute a large batch without validation. Use a two- or three-slide microdeck first.
9. Include only runtime features the user needs. Default to audience-view delivery with an always-discoverable Author section in the unified menu, author text editing, a contextual per-element toolbar for text and safe visual styles, a full typography editor constrained to approved families and semantic size/leading bounds, keyboard navigation, deep links, unsaved-change status, light/dark/custom themes, edit preservation, and reduced-motion support. These are supplied by the protected PPT Studio runtime, not reimplemented per deck.
10. Audit the final rendered HTML text after browser edits; do not trust only the earlier content plan.
11. Treat the first generated deck as a professional first draft, not a generic layout sample. Use the approved voice, evidence, visual forms, brand hierarchy, anchor slides, and audience decision to make each page specific.
12. A static pass or a few representative screenshots never prove visual quality. Every slide, every required state including state zero, every theme, and every required viewport must pass rendered geometry QA and an explicit harmony review before delivery.

## Phase 0: Detect mode and initialize

Detect one mode:

- `new`: create a presentation from sources, notes, or a topic.
- `enhance`: preserve and improve an existing HTML deck.
- `convert`: convert PPTX, documents, spreadsheets, or reports into a web deck.

If no project contract exists, run:

```bash
python3 scripts/init_project.py <output-directory>
```

Read [conversation-flow.md](references/conversation-flow.md). Announce the four macro stages, then ask only the first question.

## Phase 1: Purpose, audience, and decision

Collect presentation type, audience, prior knowledge, expected decision, desired post-presentation discussion, objections, presentation time, and reading-versus-speaking use.

Do not accept vague audience labels without helping the user clarify decision power, interests, concerns, and context. Record answers in `project`, `audience`, and `objective`.

## Phase 2: Resources and brand

Read [brand-research.md](references/brand-research.md). Record a visible brand-usage policy, not only colors and logo files. The policy must define brand names, allowed marks, repetition limits, footer behavior, textual-mention styling, and slide-specific exceptions.

Request brandbook, logos, prior decks, official site, fonts, colors, documents, data, images, and references. Evaluate quality. When assets are missing or poor, search official sources for better versions and brand evidence. Distinguish confirmed facts from inference. Present a short brand-direction summary and wait for approval.

## Phase 3: Speaker voice and expert perspective

Read [voice-and-story.md](references/voice-and-story.md) and [expert-research.md](references/expert-research.md).

Before drafting content, request a real writing or speaking sample when available. Generate three small title families using the user's real subject, then ask which sounds most like the presenter. Record preferred and rejected language.

Recommend the primary expert role, complementary roles, and the audience-side evaluator. Ask the user to confirm or complement them.

## Phase 4: Structure and content co-creation

Read [content-planning.md](references/content-planning.md).

Ask whether the user already has a structure. If yes, extract and critique it. If not, propose a narrative and explain what information each section requires. Choose the clearest representation for each information shape.

For every slide record:

- purpose;
- audience takeaway;
- evidence and source;
- proposed content;
- recommended visual form;
- speaker notes;
- uncertainty or missing information.

Show the outline and content review. Wait for explicit approval.

## Phase 5: Research and content finalization

Activate research when evidence is missing, unstable, specialized, or high stakes. Research as the confirmed subject-matter expert. Prefer primary, official, recent sources and record URLs, dates, claims, and confidence.

Ask additional questions rather than inventing facts. Separate facts, calculations, estimates, assumptions, and recommendations. Present the final content for confirmation or editing. Set `approvals.content` only after confirmation.

## Phase 6: Visual exploration

Read [visual-exploration.md](references/visual-exploration.md) and [resource-routing.md](references/resource-routing.md).

Recommend two options when brand direction is strong and three when visual uncertainty is meaningful. Build the same two- or three-slide microdeck in every option. Prefer one self-contained comparison gallery. Every option must use the protected runtime, and the gallery must render every representative slide in a sandboxed, non-interactive iframe with its own controls hidden. Never place live microdeck toolbars inside the comparison interface.

Immediately validate the generated gallery with `scripts/qa_gallery.cjs`. The first option must load without a user click, every preview must fill its 16:9 frame, labels must use `Opción A-1`, `Opción A-2`, and equivalent notation, and all options must pass desktop, laptop, phone portrait, and phone landscape rendering before the gallery is shown.

Do not create the full deck until the user selects a direction or approves a combined revision.

## Phase 7: Delivery routing, feature selection, and production

Read [delivery-routing.md](references/delivery-routing.md), [runtime-features.md](references/runtime-features.md), [theme-system.md](references/theme-system.md), [host-compatibility.md](references/host-compatibility.md), and [licensing-and-attribution.md](references/licensing-and-attribution.md).

Before full production, infer whether hosting or a native presentation format would materially help this project. Ask one concise delivery question with only the routes that are both relevant and available. Record the evaluation and the user's selection in `delivery.route_evaluation`. Do not repeat the question when the user already settled the delivery route.

Self-contained HTML remains the canonical PPT Studio output and the only design/runtime owner. Optional routes are additive workers: they consume the approved contract and validated HTML, but may not redesign the deck, replace its runtime, weaken its QA, or block HTML delivery if they fail. Publishing, connecting a provider, installing a tool, or creating an external artifact always requires explicit approval.

Confirm only relevant optional features. Begin every full deck by copying `assets/runtime/base-deck.html` into the output file. Generate on its fixed 1920 x 1080 stage scaled uniformly to the viewport. Do not reflow slide content on phones. Embed required images, icons, CSS, JS, and licensed fonts in the final file whenever feasible. Do not import external presentation frameworks or require other skills.

Treat the copied runtime as protected infrastructure. Replace its sample slides and extend its design tokens and layout CSS, but preserve the runtime metadata, `data-ppt-studio-runtime="base-deck-v2"`, stage scaling, `prev · counter · next · menu` control order, audience/author separation, save workflow, theme dialog, Help and About dialogs, attribution block, edit baselines, and navigation script. Do not create a separate menu, navigation, save, theme, or keyboard runtime that merely resembles these features. Add approved optional modules as extensions to this runtime.

Keep a deterministic generator, normally `.work/build_presentation.py`, for structural changes. Never overwrite a saved browser-edited deck directly. Generate a fresh candidate, then preserve changed editable fields and create a backup with:

```bash
python3 scripts/preserve_edits.py presentation.html .work/presentation-generated.html --output presentation.html
```

Use stable `data-edit-id` values across regeneration. If a browser-edited ID is intentionally removed, stop and reconcile it explicitly rather than dropping the edit silently.

After producing or materially revising a full deck, run the strict runtime check and fix every error before presenting it for review:

```bash
python3 scripts/validate_html.py presentation.html --strict
```

Every user-facing slide text node must have a stable `data-edit-id`. Classify internal states as `required`, `on-demand`, `speaker-only`, or `decorative`. Arrow navigation must consume remaining `required` states before changing slides. Deliver audience mode by default. Keep the Author section visible so editing and saving are discoverable; author actions explicitly transition into author mode. `?author=1` and `E` remain direct shortcuts, and saved copies reset their active state to audience mode.

Annotate layout semantics for rendered QA:

- `data-qa-box` on every independent visual block;
- `data-qa-role="header|content|footer|brand|connector|decoration"` on major regions;
- `data-qa-anchor` on nodes connected by a visual line;
- `data-qa-connector-for="anchor-a anchor-b"` on connectors;
- `data-qa-connector-group="group-name"` on related connector segments that must share length, thickness, and axis;
- `data-qa-connector-geometry="strict"` when a connector must terminate exactly at two declared anchors;
- `data-qa-text-stack="balanced"` on vertical text groups whose inter-element rhythm must be checked;
- `data-brand-mark` on visible logos or wordmarks;
- `data-brand-mention` on intentional textual brand mentions.

Overlap is forbidden by default. Use `data-qa-overlap="allow"` only for deliberate containment or layering and explain the exception in the project contract. Flex and grid children must use `min-width:0` and `min-height:0` where content could otherwise force overflow.

## Phase 8: Motion workflow

Read [motion-workflow.md](references/motion-workflow.md).

After static design stabilizes:

1. Translate vague motion language into precise vocabulary.
2. Find at most five to seven high-conviction opportunities and record rejected candidates.
3. Ask the user which opportunities to implement.
4. Implement exact motion recipes.
5. Audit purpose, frequency, easing, duration, physicality, interruptibility, performance, accessibility, and cohesion.
6. Apply only approved improvements.

## Phase 9: Final QA and delivery

Read [quality-gates.md](references/quality-gates.md) and [visual-qa.md](references/visual-qa.md).

Before delivery:

1. Require the current HTML to be saved.
2. Extract visible text from the final HTML with `scripts/extract_visible_text.py`.
3. Check spelling, accents, punctuation, names, dates, numbers, currencies, acronyms, terminology, and duplicates.
4. Show sensitive corrections for confirmation.
5. Re-render after text corrections and check overflow again.
6. Run `scripts/qa_runtime.cjs` against the final file. It must enumerate every slide and every required state, including state zero, rather than sampling representative pages.
7. Require text-to-text, surface-to-text, multiline line-height, annotated text-stack spacing, connector proportion, and connector endpoint geometry checks to pass.
8. Inspect the generated screenshot gallery for balance, closure, intentional whitespace, connector integrity, footer/chrome clearance, and brand restraint. Record the completed harmony review in `visual_qa.harmony_review`.
9. Render desktop, laptop, phone portrait, and phone landscape viewports in audience mode; also inspect author mode, every theme, every dialog, and optional module.
10. Validate the project contract and HTML in strict mode; geometry failures, incomplete harmony review, or a runtime-contract error block delivery.
11. Execute only the approved optional delivery routes. Validate each derivative independently, report fidelity or security limitations, and preserve the validated HTML even when a derivative cannot be completed.

Use:

```bash
python3 scripts/validate_project.py presentation-project.json --phase delivery
python3 scripts/validate_html.py presentation.html --strict
node scripts/qa_runtime.cjs presentation.html --project presentation-project.json
```

Do not open a browser automatically. Start a local server only when needed and give the user its URL.

## Approval gates

Never bypass these gates:

1. `approvals.brand`
2. `approvals.voice`
3. `approvals.expert_mode`
4. `approvals.structure`
5. `approvals.content`
6. `approvals.style`
7. `approvals.features`
8. `approvals.final_text`

If a complete source deck already settles a gate, summarize the inferred decision and request a concise confirmation instead of repeating discovery.

## Project artifacts

Maintain:

```text
presentation-project.json
content-approved.md
style-decision.json
feature-selection.json
presentation.html
```

Embed a copy of the current project contract inside the final HTML as:

```html
<script type="application/json" id="presentation-project-data">...</script>
```

## Implementation and licensing

PPT Studio is an original, self-contained Apache-2.0 implementation developed by intellbits. External repositories may be evaluated as conceptual references, but never copy their source, templates, assets, or instruction files into an output or into this plugin. Do not require users to install another presentation skill. Preserve the supplied generator metadata, About panel, license notice, and attribution in redistributed runtime or source packages. Do not add a permanent intellbits mark to presentation slides unless the user explicitly requests it. Respect the separate trademark rules in `TRADEMARKS.md`.

## Resource map

- [conversation-flow.md](references/conversation-flow.md): progressive interview UX.
- [brand-research.md](references/brand-research.md): asset and visual-direction validation.
- [voice-and-story.md](references/voice-and-story.md): human voice and title calibration.
- [expert-research.md](references/expert-research.md): expert selection and research.
- [content-planning.md](references/content-planning.md): narrative and slide contracts.
- [visual-exploration.md](references/visual-exploration.md): microdeck comparison.
- [runtime-features.md](references/runtime-features.md): editing, saving, controls, and state navigation.
- [delivery-routing.md](references/delivery-routing.md): inference, user confirmation, optional hosting, native formats, and host equivalents.
- [theme-system.md](references/theme-system.md): light, dark, and brand-custom presentation themes.
- [host-compatibility.md](references/host-compatibility.md): capability-based behavior across Codex, ChatGPT, Claude Code, and Claude Chat.
- [licensing-and-attribution.md](references/licensing-and-attribution.md): content ownership, runtime notices, and intellbits brand boundaries.
- [motion-workflow.md](references/motion-workflow.md): restrained presentation motion.
- [quality-gates.md](references/quality-gates.md): content, visual, technical, and text QA.
- [visual-qa.md](references/visual-qa.md): rendered geometry, state completeness, brand density, and harmony review.
- [resource-routing.md](references/resource-routing.md): bundled visual engines and export routes.
