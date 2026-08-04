# Visual exploration

## Decide option count

- Recommend two options when brand direction is strong or the deck is conservative.
- Recommend three when visual uncertainty is material or the decision is high stakes.
- Recommend one when enhancing an established deck or following an exact reference.

Ask whether the user wants two, three, or the recommended direction only.

## Build a fair microdeck

Use identical approved content across options. Build no more than three slides per option:

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

Prefer one self-contained HTML gallery with isolated previews. Use `scripts/make_preview_gallery.py` when options are separate HTML files. The gallery must identify A, B, and C clearly and allow keyboard switching.

Describe each direction with:

- visual thesis;
- best use;
- tradeoff;
- typography;
- palette;
- motion character.

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
