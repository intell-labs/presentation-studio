# Brand and resource validation

## Resource request

Ask for the smallest useful set first:

1. Brandbook or design guidelines.
2. Logo, preferably SVG or transparent PNG.
3. Official website.
4. Prior presentation or marketing material.
5. Source documents, spreadsheets, images, and partner logos.

Example: `Puedes compartir un brandbook, una presentación anterior o simplemente el logo y sitio web.`

## Quality assessment

For every resource record:

- purpose;
- source or local path;
- resolution or format;
- usability: `usable`, `replace`, or `reference-only`;
- reason;
- rights or confidentiality concerns.

Reject low-resolution logos, screenshots with unreadable text, outdated brand marks, accidental white backgrounds, and assets with uncertain provenance.

## Internet recovery

When supplied resources are poor or missing:

1. Search the official website, newsroom, press kit, investor relations, developer brand page, or official social account.
2. Prefer official SVG or high-resolution transparent PNG.
3. Look for an official brand manual before inferring a system.
4. If no manual exists, infer palette, typography, spacing, photography, iconography, and tone from multiple official pages.
5. Use third-party brand repositories only as fallback and label them clearly.
6. Never present an inferred element as confirmed.

Record URL, retrieval date, file type, and confidence.

## Brand-direction confirmation

Present no more than six concise lines:

```text
Línea visual identificada
Logo: official SVG from [source]
Palette: confirmed / inferred
Typography: confirmed / closest available alternative
Visual character: concise description
Recommended deck direction: concise description
```

Ask: `¿Confirmas que utilicemos esta dirección?`

Do not start visual exploration until the user approves or corrects the brand direction.

## Self-contained output

Download approved assets into the project. Do not leave fragile hotlinks in the final deck. Optimize oversized images, preserve transparency, and embed final assets as data URLs when building a standalone HTML file.
