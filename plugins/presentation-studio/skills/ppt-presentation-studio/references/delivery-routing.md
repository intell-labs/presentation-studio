# Delivery routing

PPT Studio owns the presentation strategy, content, visual system, self-contained HTML, and runtime. Hosting and native-presentation tools are optional delivery workers, never competing design systems.

## Infer before asking

Evaluate these routes after content and visual direction are approved, before full production:

| Route | Recommend when | Usually skip when |
| --- | --- | --- |
| Self-contained HTML | Always. It is the canonical PPT Studio artifact. | Never. |
| Hosted site | The user needs a shareable URL, remote or mobile access, controlled access, a custom domain, or managed distribution. | The user needs only a local/offline file, already chose their own hosting, or no hosting capability is available. |
| Native presentation | The user needs editable PPTX or Google Slides, corporate handoff, or an offline presentation workflow. | HTML interaction and visual fidelity are primary and no native file is required. |

Infer usefulness from the brief and current environment. Do not present unavailable routes. If a route is useful but unavailable, offer a small manual handoff rather than installing or connecting a provider without permission.

## Required delivery checkpoint

Ask one concise question. Recommend the smallest useful route and state one tradeoff.

Example when hosting helps:

> La presentación HTML ya será el archivo principal. Como necesitas compartirla desde el teléfono, también recomiendo publicarla como sitio privado. ¿La entregamos solo como HTML o HTML + enlace privado?

Example when a native file helps:

> El HTML conservará mejor la experiencia. Como tu equipo también necesita editar en PowerPoint, ¿agregamos una versión PPTX sabiendo que algunas interacciones pueden simplificarse?

Example when neither adds value:

> Para este caso el HTML autocontenido es suficiente y evita trabajo duplicado. ¿Confirmamos entrega solo en HTML?

Do not ask again when the user already requested a route. Record:

- host and capability availability;
- recommendation and reason for each route;
- user-selected routes;
- explicit approval and notes.

## OpenAI and Codex routing

Use capabilities when present; never make them dependencies of the core skill.

- Use Sites for an approved hosted-site route. Publish only the already validated deck or a minimal hosting wrapper. Do not let website scaffolding alter slide layout, navigation, content, or runtime. When `.openai/hosting.json` exists, follow the Sites build and hosting workflow.
- Use Presentations for an approved native-presentation route. Rebuild the approved content as PPTX or Google Slides separately, preserve brand and narrative decisions, run native-format QA, and report any fidelity differences from HTML.
- If a capability is absent, keep the HTML delivery and provide a provider-neutral handoff.

## Claude routing

Route by outcome because Claude surfaces and plan availability change.

- In Claude Chat, use Artifacts publishing or organizational sharing only when it is available and the user approved a hosted route. Confirm the actual visibility before publishing. Do not treat an Artifact as managed authentication, persistent storage, custom-domain hosting, or an external API backend unless the current host explicitly provides those capabilities.
- Use Claude's file-creation capability or a PowerPoint integration only when a native presentation route is approved and available. Generate the native deck from the approved project contract, not from a new design direction, and validate the resulting file separately.
- In Claude Code, inspect installed skills, plugins, MCP servers, and provider CLIs. For hosting, use only an already configured provider or approved integration. For native slides, use an available PPTX/Slides tool. Never install, connect, authenticate, or publish without the user's approval.
- If no equivalent capability exists, deliver the self-contained HTML plus the smallest manual handoff.

## Non-interference rules

1. Finish and validate the canonical HTML independently.
2. Never merge another presentation runtime, template system, navigation layer, or style owner into it.
3. Optional workers receive approved content, brand, and delivery constraints; they do not reopen settled design decisions.
4. Each derivative has its own QA and limitation report.
5. Failure of hosting or native conversion does not invalidate or overwrite the HTML.
6. Never embed hosting credentials, access tokens, or real secrets in the deck.
7. Distinguish a client-side access gate from authenticated hosting before promising confidentiality.
