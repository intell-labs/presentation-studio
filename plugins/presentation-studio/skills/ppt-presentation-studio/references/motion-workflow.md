# Motion workflow

Use motion as orientation, feedback, state explanation, or a bridge across change. Restraint is mandatory.

## 1. Translate natural language

When the user describes motion vaguely, map it to a precise term before planning it. Useful vocabulary includes fade, scale in, reveal, stagger, orchestration, origin-aware animation, crossfade, continuity transition, layout animation, accordion, direction-aware transition, hover effect, press feedback, spring, number ticker, mask, line drawing, and reduced motion.

If multiple terms fit, explain the difference briefly and ask only when the choice changes the result.

## 2. Find opportunities

Inspect the stable HTML and record both accepted and rejected candidates. A candidate must pass:

1. Frequency: repeated interactions receive less motion.
2. Purpose: feedback, spatial consistency, state indication, preventing a jarring change, explanation, or rare delight.
3. Speed: the effect fits a modest time budget.
4. Function: motion improves comprehension rather than distracting from content.

Return at most five to seven opportunities, ordered by leverage. Include exact properties, duration, easing, pointer conditions, and reduced-motion behavior.

Typical presentation budgets:

- press feedback: 100-160ms;
- hover highlight: 160-220ms;
- small menu: 150-220ms;
- details panel: 200-320ms;
- slide transition: short, direction-aware, and non-blocking;
- stagger: 30-70ms between items.

Prefer `transform` and `opacity`. Avoid layout-thrashing properties and `transition: all`. Gate hover with `@media (hover: hover) and (pointer: fine)`.

## 3. Ask for selection

Do not implement the full opportunity list automatically. Show the shortlist and rejected candidates. Ask which ones make sense for the presentation.

## 4. Implement

Use shared motion tokens. Ensure animations can be interrupted or immediately completed when navigation changes. Never hide readable content if the animation runtime fails.

For data and dense content:

- keep values readable at rest;
- animate entrance once, not continuously;
- avoid decorative mouse tracking;
- prefer highlight, shadow, color, and at most 2px translation on hover.

## 5. Audit improvements

After implementation, audit:

- purpose and frequency;
- easing and duration;
- physical origin;
- interruptibility;
- frame performance;
- reduced-motion behavior;
- consistent tokens;
- missed high-value opportunities.

Prioritize findings by impact divided by effort. Ask the user which findings to apply before another broad modification.

## 6. Verify

- Feel-check in real navigation, not only code.
- Confirm rapid next/previous input never leaves partial states.
- Confirm menus and accordions reverse cleanly.
- Confirm hover never traps touch users.
- Confirm reduced-motion produces a gentler immediate state.
- Confirm no text or data moves while being read.
