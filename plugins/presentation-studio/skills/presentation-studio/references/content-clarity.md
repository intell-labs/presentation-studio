# Audience clarity and semantic figures

Use this reference when reducing a deck, planning a diagram, adding numerical
assumptions, or opening secondary detail. It is not a prescribed visual style.

## Priority before density

Assign each statement main / supporting / detail, and audience / presenter-only.
Keep the decision, comparison basis, uncertainty, scope and material caveats visible.
Move only genuinely secondary explanation into a modal or notes. Executive variants
map original claims to retained/combined/omitted claims; retain curated vocabulary
and essential meaning. Never shorten by shrinking all type or compressing every card.
Use role-specific budgets under `design_contract.readability.by_role`; for example
`{"cover":{"max_words_per_slide":24}}` is a proposed project choice, not a default.

Before a diagram, write its actors, relationships and takeaway. Choose a comparison,
process, hierarchy, architecture or trend from that structure. SVG/HTML illustrations
should explain relationships, not simulate generic UI with decorative bars. Mark any
illustrative data explicitly. A pretty connector is not evidence of a causal link.

Recheck each rendered title, term, client name and figure in audience mode. Presenter
prompts belong in notes, not visible client copy. Do not invent approved commercial
terms, labels or financial certainty to make a slide sound decisive. Ask one question
when ambiguity would change meaning. Preserve the user's approved wording otherwise.

## One model for linked numbers (optional module)

Use `assets/runtime/numeric-model.js` only when a deck has related figures or an
assumption calculator. Inline the original module after a JSON script with ID
`presentation-numeric-data`; no runtime dependency/download. Define **all** displayed
dependent values there, not a second handwritten number in a card or graph.

Every node requires `id`, human `label`, semantic `meaning` (saving, cost, volume,
productivity, etc.), dimensional `unit`, display `unit_label`, `period`, `status`
(observed / assumption / estimate) and `source` (mandatory for observed facts).
Inputs have a finite `value`, optional bounds and decimals; derived nodes have
`operation` (add/subtract/multiply/divide) and two dependency IDs in `args`.
Unit exponents cancel through arithmetic. No dynamic formula execution is allowed.

```json
{"locale":"es-SV","nodes":[
 {"id":"saving","label":"Ahorro mensual","meaning":"saving","value":55000,
  "unit":{"USD":1,"month":-1},"unit_label":"USD / mes","period":"Escenario mensual",
  "status":"assumption","source":null,"min":0},
 {"id":"volume","label":"Volumen mensual","meaning":"volume","value":400000,
  "unit":{"package":1,"month":-1},"unit_label":"paquetes / mes","period":"Escenario mensual",
  "status":"assumption","source":null,"min":1},
 {"id":"saving-per-package","label":"Ahorro por paquete","meaning":"saving",
  "operation":"divide","args":["saving","volume"],"decimals":4,
  "unit":{"USD":1,"package":-1},"unit_label":"USD / paquete","period":"Escenario mensual",
  "status":"estimate","source":null}
]}
```

This example yields $0.1375 **saving per package**, not cost per package. It is a
regression example, never a recommended business assumption. A rate multiplied by
12 is annualized, not automatically realized first-year savings: mark the derived
node `aggregation:"annualized"` with the actual period; the module emits a visible
qualification. Conversion durations must themselves carry their dimensional unit.
Do not treat an assumption-derived result as an observed fact.

Bind each repeated value and its local meaning/context:

```html
<div data-metric="saving-per-package">
  <span data-metric-label="saving-per-package"></span>
  <output data-metric-value="saving-per-package"></output>
  <small data-metric-context="saving-per-package"></small>
</div>
```

Generated outputs are read-only; edit the source assumption, not the computed text.
Use labelled numeric inputs with `data-metric-input="volume"` only on assumption
nodes. A valid change recalculates all bindings, updates embedded JSON and marks the
deck dirty. Invalid inputs leave the last valid model intact and show an error.
Test changed assumptions, zero denominators, dimensions, bounds, non-finite values,
dependent outputs and save/reopen. Custom charts must consume the same evaluated
model and be tested separately; the module does not generate arbitrary charts.

## Summary-first detail

Use native `<dialog class="ps-dialog" id="..." aria-labelledby="...">` outside the
scaled stage, opened by a button `data-dialog-open="..."`. Include:

- a heading with the accessible label ID and a `data-dialog-close` button;
- `data-dialog-summary` with the useful interpretation first;
- optional `data-dialog-edit` button and a `data-dialog-editor hidden` section for
  labelled assumption inputs. Do not make inputs the first thing the reader sees.

Use content-sized width/height with viewport limits and internal vertical scrolling.
Avoid filling empty space with oversized cards, duplicate tables or repeated labels.
The protected runtime suppresses deck shortcuts while modal, closes on Escape or
backdrop, and restores focus to the opener. Opening/reopening resets editing to the
summary. Test focus/Tab, close, keyboard navigation, scrolling, viewport containment,
and input updates on desktop and phone. Annotate modal prose with `data-qa-text` for
contrast inspection; content still needs explicit visual/editorial review.

## Semantic color and honest QA

Define project-level foreground/background pairs by surface and purpose (action,
risk, data, supporting text). Preserve exact brand base colors independently of
readable text colors; use appropriate accessible variants for small copy. No color
pair is universally required. Check the actual composited background in each theme.

QA measures simple solid/alpha backgrounds, circle containment, declared clearances
and shared regions. Photos, gradients, complex overlays and unannotated shapes are
listed as unmeasured, not passed; inspect them visually. It cannot certify the truth
of business inputs, human hierarchy or all WCAG criteria. Report limits separately
from technical success, and keep essential interpretation visible without a modal.
