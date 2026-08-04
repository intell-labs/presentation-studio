# HTML runtime features

## Defaults

Include by default:

- fixed 1920 x 1080 stage scaled uniformly;
- keyboard and button navigation;
- `#hoja-NN` deep links;
- editable user-facing text;
- discreet controls menu;
- unsaved-change indicator;
- save and save-as workflow;
- light, dark, and brand-custom themes;
- light mobile controls;
- fullscreen;
- reduced-motion support.

Ask only about optional features that are relevant: notes, presenter view, timer, overview, login, offline font embedding, PDF, PPTX, or generated illustrations.

## Controls menu

Keep primary previous/next navigation visible. Put authoring and utility commands behind a discreet ellipsis or sliders button and the `M` or `?` shortcut.

Possible items:

- Edit text;
- Save;
- Save as;
- Notes;
- Presenter view;
- Timer;
- Overview;
- Export PDF;
- Export PPTX;
- Appearance: Light, Dark, Brand;
- Edit brand theme;
- Fullscreen;
- Licenses and source;
- Keyboard help.

Hide unavailable modules rather than showing dead controls. Theme switching belongs inside this menu and may also use `T` as a keyboard shortcut.

## Editing contract

Every user-facing string must have a stable `data-edit-id`. Controls, generated page counters, speaker-only notes, and legal metadata are excluded unless explicitly editable.

When edit mode begins:

- make editable nodes contenteditable;
- show a clear but unobtrusive edit state;
- mark the document dirty on `input`;
- display `Cambios sin guardar`;
- prefix the browser title with a dot when dirty;
- warn before unload.

## Save behavior

The browser cannot infer and overwrite an arbitrary local path without user permission.

Use this order:

1. If a previously authorized file handle exists, write to it on `Cmd/Ctrl+S`.
2. Otherwise offer `Vincular archivo actual` or `Guardar como…` through the File System Access API when available.
3. If unsupported or denied, download a complete updated HTML copy.
4. Never claim a fallback download overwrote the original.

Serialize the current DOM, including user edits and embedded project data, while removing transient open-menu and edit-mode states.

Theme changes are document changes. Mark them dirty, serialize the selected theme and custom tokens, and include them in downloaded or directly saved HTML.

## Internal states and arrow navigation

Classify every hidden or progressive state:

- `required`: part of the presentation path;
- `on-demand`: opened only through an explicit trigger;
- `speaker-only`: notes or presenter material;
- `decorative`: never consumes navigation.

On next:

1. reveal the next unrevealed `required` state;
2. otherwise move to the next slide.

On previous:

1. reverse the last revealed `required` state;
2. otherwise move to the previous slide at its final required state.

Support `#hoja-05/estado-02`. Ensure controls, deep links, overview, and exported state remain consistent.

## Export behavior

- PDF may use browser print or a bundled render script; motion becomes static.
- PPTX is optional because it adds weight and may reduce fidelity. Include its module only after confirmation.
- For progressive states, ask whether export should use final state only or split required states into separate pages.

## Mobile

Do not reflow slide content. Scale the fixed stage. On narrow screens show only previous and next controls by default; keep utilities in the menu.

## Themes

Read `theme-system.md`. Every generated deck includes light, dark, and custom theme support unless the user explicitly requests a single locked theme. Never implement dark mode with CSS inversion.
