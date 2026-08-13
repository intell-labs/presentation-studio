# Visual exploration

## Decide option count

- Recommend two options when brand direction is strong or the deck is conservative.
- Recommend three when visual uncertainty is material or the decision is high stakes.
- Skip new alternatives only when enhancing an established deck or following an exact approved reference; record why exploration is unnecessary.

Ask whether the user wants two, three, or the recommended direction only.

## Build a fair microdeck

Use identical approved content across options. Build two or three slides per option:

1. cover or opening;
2. representative narrative/content slide;
3. data, comparison, or process slide when relevant.

A cover alone is insufficient because it does not prove that the system handles real information.

## Direction families

Choose contextually distinct options, commonly:

- brand-first executive;
- editorial or narrative;
- data-first or Swiss;
- presenter-led cinematic;
- restrained template system.

Do not label options inside the slide artwork. Identify them in the comparison interface.

## Comparison artifact

Prefer one self-contained HTML gallery with isolated previews. Each option must be a complete `base-deck-v2` microdeck, not loose slide markup. Use `scripts/make_preview_gallery.py` when options are separate HTML files. The gallery shows all representative slides for the selected direction at once in sandboxed iframes, disables iframe interaction, and hides every internal menu, arrow, status, dialog, and author control. The only gallery controls are the A/B/C direction tabs. Never overlay comparison UI on slide artwork.

Preview names must be addressable in conversation: `Opción A-1`, `Opción A-2`, `Opción A-3`, then `Opción B-1`, and so on. Do not use generic labels such as “vista representativa.”

The first option must initialize its iframes only after their responsive containers have layout dimensions. A gallery that requires toggling A/B before slides appear, or whose fixed-stage preview is scaled from an iframe's default detached size, is broken.

Example:

```bash
python3 scripts/make_preview_gallery.py option-a.html option-b.html option-c.html \
  --labels "A · Ejecutiva" "B · Editorial" "C · Datos" \
  --descriptions "Marca y decisión" "Relato y ritmo" "Comparación rigurosa" \
  --output visual-options.html
```

Run rendered gallery QA before asking for a selection:

```bash
node scripts/qa_gallery.cjs visual-options.html --output-dir work/gallery-qa
```

The gallery gate covers every option at desktop, laptop, phone portrait, and phone landscape. It blocks on unloaded or blank iframes, exposed microdeck controls, incorrect stage scaling, non-16:9 frames, horizontal overflow, undersized tabs, missing option-slide names, and compact layouts that fail to become one readable column.

Describe each direction with:

- visual thesis;
- best use;
- tradeoff;
- typography;
- palette;
- motion character.

Reject a direction before showing it if it merely swaps colors or fonts. Options must differ in information hierarchy, composition, density, chart treatment, and motion character while preserving identical content.

## Generated illustrations

Keep generated imagery off by default. When explicitly requested:

1. ask which slides benefit;
2. recommend one to three high-value images;
3. confirm type and style;
4. generate at the exact placement ratio;
5. validate text, logos, and factual content separately.

Use approved brand assets, official imagery, CSS, inline SVG, and icons when generated illustration is not requested.

## Selection

Allow the user to select one direction or name specific traits to combine. If combining, create one revised preview before building the full deck. Set `approvals.style` only after that preview is approved.
