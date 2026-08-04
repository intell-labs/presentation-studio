# Conversation flow

## Start

Explain the process in four short stages, promise step-by-step validation, then ask only the first question.

## Question format

Use this shape for non-obvious questions:

```text
Paso N · Short label
Question?

- Option: one-line explanation.
- Option: one-line explanation.
- Option: one-line explanation.

Ejemplo: “A context-specific answer.”
Recomendación: only when evidence supports one.
```

Never ask more than one decision per message. Do not dump the full interview. If a user answers multiple future questions voluntarily, record them and skip those turns.

## Presentation-type options

Offer four to six relevant options, selected from:

- Pitch or investment: obtain funding, partnership, or approval.
- Commercial proposal: sell a solution or close a project.
- Financial or board: support an executive decision with evidence.
- Corporate profile: explain a company, group, capability, or track record.
- Product or launch: explain a solution and why it matters.
- Training: develop knowledge or a skill.
- Conference or keynote: inform, persuade, or inspire a live audience.
- Technical or research: communicate evidence, methods, or architecture.
- Internal report: align a team on status, risks, and next actions.

Example: `Propuesta financiera para solicitar una línea de crédito.`

## Audience questions

Progress from simple to specific:

1. Who will attend?
2. Who can approve or block the decision?
3. What do they already know?
4. What do they care about most?
5. What concerns or objections are likely?

Example: `Comité de crédito; conocen la empresa, pero necesitan claridad sobre repago, garantías y exposición total.`

## Outcome questions

Ask separately:

- What action or decision should follow?
- What should dominate the discussion afterward?
- What one idea should remain the next day?

Example: `Aprobar una línea de $400k y acordar el proceso de desembolso.`

## Adaptive behavior

- If sources already answer a question, summarize the inferred answer and ask for confirmation.
- If the user is uncertain, recommend a default and explain the consequence in one sentence.
- After three to five confirmed decisions, summarize the current brief in no more than six lines.
- Record every confirmed answer in `presentation-project.json` before moving on.
- A user may pause, resume, or revise a previous answer; update downstream assumptions when that happens.

## Stop conditions

Pause when a missing choice would materially change audience strategy, content truth, visual direction, legal exposure, or delivery format. Continue with a clearly labeled assumption only when the choice is low risk and reversible.
