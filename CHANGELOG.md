# Changelog

## Unreleased

- Consolidated the product, marketplace, canonical skill, documentation, runtime metadata, and release packages under the Presentation Studio and intell labs identities.
- Moved all repository and installation references to `intell-labs/presentation-studio` and renamed the marketplace to `presentation-studio-marketplace`.
- Renamed the canonical skill to `presentation-studio` and removed obsolete public brand references.

## 1.0.4 - 2026-08-05

- Added separately labeled ChatGPT and Claude skill ZIPs while retaining a distinct Codex plugin archive.
- Added a floating contextual editor that opens beside the exact text component selected in edit mode and identifies the copy being edited.
- Added per-element quick controls for approved font family, bounded font size, text color, bold, italic, alignment, reset, and access to the full typography dialog.
- Added safe visual-component editing for fill or transparent background, border color, width and style, radius, shadow, opacity, and reset on explicitly styleable content regions.
- Added responsive bottom-sheet behavior for contextual editing on compact viewports, 44 px controls, visible selection states, viewport clamping, and Escape/slide-change cleanup.
- Added independent text-style and visual-style baselines so browser styling decisions survive structural regeneration through `preserve_edits.py`.
- Expanded rendered runtime QA to exercise contextual text and visual editing on desktop and phone portrait, including semantic size clamping, style application, reset, viewport containment, and desktop control visibility.

## 1.0.3 - 2026-08-05

- Standardized every release target on plain semantic versions (`MAJOR.MINOR.PATCH`) and removed date/build suffixes from Codex versioning.
- Added a complete per-element typography editor with approved-family selection, bounded size, weight, leading, tracking, alignment, italic, reset, and the `Alt/⌥ Y` shortcut.
- Added semantic font-size bounds and rendered QA failures for undersized or oversized labels, body copy, H3, H2, and H1 text.
- Made the Author section permanently discoverable in the controls menu while preserving audience as the serialized default state.
- Added visible shortcut badges beside every menu action with an implemented key and aligned `?`, `M`, save, and save-as behavior with their labels.
- Locked approved brand palettes across light, dark, and custom themes so theme switching cannot replace brand colors with pastel or tinted variants.
- Added inverse key-slide polarity: dark anchors in light mode and light anchors in dark mode, with exact brand accents preserved.
- Added rendered QA gates for menu discoverability, shortcut labels, theme polarity, and locked brand-color invariance.
- Added rendered text-to-text and text-to-surface collision checks, readable multiline line-height bounds, and balanced spacing checks for related text stacks.
- Added strict connector endpoint, axis, thickness, and proportional-length validation for diagrams and timelines.
- Reworked preview galleries so the first direction loads reliably without a tab toggle, every preview has an addressable name such as `Opción A-1`, and hidden directions load safely when selected.
- Forced representative previews to their fully revealed state and added a gallery QA failure for required content that remains hidden or visually subdued.
- Added responsive gallery layouts for desktop, laptop, phone portrait, and phone landscape, plus a dedicated `qa_gallery.cjs` delivery gate.
- Corrected preview-mode runtime sizing so embedded slides fill and center inside responsive 16:9 cards without reserving space for hidden presentation controls.

## 1.0.2 - 2026-08-04

- Renamed the canonical skill from its original working name to its current public identity for easier discovery in ChatGPT, Codex, Claude Code, and Claude Chat.
- Renamed the Claude Chat release archive and updated all package paths, invocations, documentation, and validators.
- Replaced the presentation runtime with the `base-deck-v2` contract: one bottom-right control cluster, an icon menu anchored upward and left, audience-safe delivery, explicit author mode, arrows-only mobile chrome, and stronger accessibility preferences.
- Rebuilt visual exploration so every microdeck is isolated in sandboxed previews with its internal controls removed.
- Added browser-edit baselines, safe file binding, backups, and `preserve_edits.py` so generator revisions cannot silently erase text changed in the browser.
- Expanded strict validation to cover runtime structure, editable-text coverage, self-contained assets, and a four-viewport visual QA matrix.
- Added rendered geometry QA for every slide and progressive state, including overlap, safe-area, connector, visible-overflow, and state-zero completion checks.
- Added explicit brand-usage policies that limit duplicate marks and textual name repetition, reject unapproved branded footers, and keep brand mentions neutral unless an exception is declared.
- Added a required harmony review so a technically valid deck cannot ship while it still feels sparse, unfinished, or visually unbalanced.

## 1.0.1 - 2026-08-04

- Added explicit developer attribution across manifests, documentation, and release packages.
- Added trademark guidance that separates open-source code rights from brand rights.
- Added generator metadata and a discreet About panel to the self-contained HTML runtime.
- Documented ownership of presentation content and third-party asset responsibilities.

## 1.0.0 - 2026-08-04

- Rebuilt the product as an original, self-contained implementation.
- Removed bundled copies of external presentation repositories.
- Added OpenAI/Codex and Claude Code plugin manifests and marketplaces.
- Added a Claude Chat skill ZIP release target.
- Added light, dark, and brand-custom presentation themes.
- Added deterministic packaging and cross-target validation.
