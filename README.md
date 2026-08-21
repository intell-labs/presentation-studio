# Presentation Studio

Plugin de **intell labs** para crear presentaciones profesionales con ChatGPT, Codex y Claude.

Convierte documentos e ideas en una presentación HTML 16:9, editable, autocontenida y lista para compartir. El proceso guía al usuario paso a paso: audiencia, marca, contenido, narrativa, diseño, producción y validación final.

[Repositorio](https://github.com/intell-labs/presentation-studio) · [Última versión](https://github.com/intell-labs/presentation-studio/releases/latest)

## Qué incluye

- Una sola skill: `presentation-studio`.
- Preguntas de definición antes de diseñar.
- Revisión de los recursos y documentos aportados.
- Opciones visuales antes de producir la presentación completa.
- Edición de textos y componentes dentro del navegador.
- Navegación, enlaces directos, temas, guardado y modo de autor.
- Validación visual en desktop, laptop y mobile.
- HTML autocontenido como formato principal.

No requiere otro framework o skill de presentaciones.

## Instalación

### Codex

```bash
codex plugin marketplace add intell-labs/presentation-studio
codex plugin add presentation-studio@presentation-studio-marketplace
```

Invocación manual: `$presentation-studio`

### Claude Code

```bash
claude plugin marketplace add intell-labs/presentation-studio
claude plugin install presentation-studio@presentation-studio-marketplace
```

Invocación manual: `/presentation-studio:presentation-studio`

### ChatGPT y Claude Chat

Descarga los archivos desde la [última versión publicada](https://github.com/intell-labs/presentation-studio/releases/latest):

- ChatGPT: `presentation-studio-<version>-chatgpt.zip`
- Claude Chat: `presentation-studio-<version>-claude.zip`

Sube el ZIP correspondiente desde la sección de Skills de cada plataforma.

## Desarrollo local

```bash
git clone https://github.com/intell-labs/presentation-studio.git
cd presentation-studio
python3 scripts/validate_all.py
python3 scripts/build_release.py --clean
```

Los paquetes se generan en `dist/`:

- Plugin para Codex.
- Skill para ChatGPT.
- Skill para Claude.
- Checksums SHA-256.

La skill principal está en:

```text
plugins/presentation-studio/skills/presentation-studio/
```

## Principios

- Una pregunta clara a la vez.
- Contenido aprobado antes de diseñar.
- Voz humana y lenguaje acorde al presentador.
- Marca consistente, sin estilos genéricos.
- Ediciones del navegador preservadas.
- Entrega bloqueada si existen desbordes, colisiones o problemas visuales.

## Licencia

Código disponible bajo Apache License 2.0. Las presentaciones y los recursos aportados continúan siendo propiedad de sus respectivos titulares.

Consulta [NOTICE](NOTICE), [TRADEMARKS.md](TRADEMARKS.md) y [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) para información legal y de atribución.

Desarrollado y mantenido por **intell labs**.
