---
name: presentation-director
description: Guide, research, plan, design, build, enhance, and validate professional presentations as self-contained HTML by default, with optional presenter tools, PDF, and PPTX. Use for new decks, pitch decks, financial or corporate presentations, reports, talks, training, product launches, converting source documents into slides, or improving an existing HTML/PPTX presentation. Use a one-question-at-a-time workflow, validate audience, brand, speaker voice, expert perspective, narrative, content, visual direction, motion, and final rendered text before delivery.
---

# Presentation Director

Create presentations through deliberate checkpoints. Prefer a portable, fixed-stage, self-contained HTML file. Do not require any other installed skill.

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
9. Include only runtime features the user needs. Default to text editing, keyboard navigation, deep links, a discreet controls menu, unsaved-change status, light/dark/custom themes, and reduced-motion support.
10. Audit the final rendered HTML text after browser edits; do not trust only the earlier content plan.

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

Read [brand-research.md](references/brand-research.md).

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

Recommend two options when brand direction is strong and three when visual uncertainty is meaningful. Build the same two- or three-slide microdeck in every option. Prefer one self-contained comparison gallery. Keep CSS isolated between options.

Do not create the full deck until the user selects a direction or approves a combined revision.

## Phase 7: Feature selection and production

Read [runtime-features.md](references/runtime-features.md), [theme-system.md](references/theme-system.md), [host-compatibility.md](references/host-compatibility.md), and [licensing-and-attribution.md](references/licensing-and-attribution.md).

Confirm only relevant optional features. Generate on a fixed 1920 x 1080 stage scaled uniformly to the viewport. Do not reflow slide content on phones. Embed required images, icons, CSS, JS, and licensed fonts in the final file whenever feasible. Use the original PPT Studio runtime; do not import external presentation frameworks or require other skills.

Every user-facing text node must have a stable `data-edit-id`. Classify internal states as `required`, `on-demand`, `speaker-only`, or `decorative`. Arrow navigation must consume remaining `required` states before changing slides.

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

Read [quality-gates.md](references/quality-gates.md).

Before delivery:

1. Require the current HTML to be saved.
2. Extract visible text from the final HTML with `scripts/extract_visible_text.py`.
3. Check spelling, accents, punctuation, names, dates, numbers, currencies, acronyms, terminology, and duplicates.
4. Show sensitive corrections for confirmation.
5. Re-render after text corrections and check overflow again.
6. Validate the project contract and HTML.

Use:

```bash
python3 scripts/validate_project.py presentation-project.json --phase delivery
python3 scripts/validate_html.py presentation.html
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
- [theme-system.md](references/theme-system.md): light, dark, and brand-custom presentation themes.
- [host-compatibility.md](references/host-compatibility.md): capability-based behavior across Codex, ChatGPT, Claude Code, and Claude Chat.
- [licensing-and-attribution.md](references/licensing-and-attribution.md): content ownership, runtime notices, and intellbits brand boundaries.
- [motion-workflow.md](references/motion-workflow.md): restrained presentation motion.
- [quality-gates.md](references/quality-gates.md): content, visual, technical, and text QA.
- [resource-routing.md](references/resource-routing.md): bundled visual engines and export routes.
