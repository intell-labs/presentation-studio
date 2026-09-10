# Mejoras de fidelidad visual — 1.1.0

El cambio responde a fallos observados al mejorar presentaciones existentes. No
impone la estética ni los clientes de un caso particular.

| Requisito | Cambio | Verificación |
| --- | --- | --- |
| R01 · Composición | Referencia, decisiones y medidas por grupos equivalentes | Geometría declarada + observación visual |
| R02 · Recursos | Inventario inicial y decisiones conservar/reemplazar/remover | Huellas de activos e identidad por slide |
| R03 · Marca completa | Decisiones sobre fondos, gradientes, iconos, superficies e imágenes | Gate de proyecto + revisión visual |
| R04 · Jerarquía semántica | Catálogo de servicios separado de tabla comparativa | Agrupación título/descripción + revisión visual |
| R05 · Portada/cierre | Roles y tonos explícitos | Contrato contra DOM antes de comprobar colores |
| R06 · Temas | Una lista para menú, teclado, guardado y QA | Dos temas; almacenamiento antiguo; exportación y reapertura |
| R07 · Evidencia | Cinco estados de evaluación separados | Huellas de HTML, decisiones, reporte y capturas; revisión por slide |
| R08 · Legibilidad | Perfil para reunión/lectura y límites propios | Densidad/tamaño + juicio visual; sin prometer legibilidad física automática |
| R09 · Casos | Cliente, proyecto, función, evidencia y confirmación | Campos y referencias; la relación comercial requiere confirmación |
| R10 · Logos | Contenedor configurable y proporciones conservadas | Identidad, visibilidad y contain; tratamiento óptico visual |
| R11 · Reproducibilidad | Fuente canónica, preservación de cambios y espera observable | Fixture repetible; menú con animación real; regresión del editor |

## Pruebas

```bash
python3 scripts/validate_all.py
node tests/runtime/edit_mode.cjs
node tests/runtime/design_contract.cjs
node tests/runtime/clarity.cjs
node tests/runtime/contrast.cjs
```

Los tests de navegador requieren Playwright y Chrome. Se ejecutan sin abrir ventanas.
El fixture anónimo reproduce una reducción de 15 organizaciones a 6, cinco logos
conservados y uno nuevo, cinco servicios, dos temas y portada/cierre invertidos.
Los tests negativos quitan/cambian/ocultan logos, borran anchors, añaden un tema,
alteran dimensiones y reutilizan evidencia de otra versión.

El inventario automático cubre imágenes y SVG inline, no todos los fondos CSS.
La calidad visual no se certifica con un contador de errores. El reporte automático
deja esa aprobación pendiente hasta inspeccionar las capturas reales.

Los HTML exportados anteriormente no se reescriben al actualizar el plugin.
La migración del contrato 1.4 a 1.5 se realiza dentro de una mejora solicitada,
preservando los textos y recursos aprobados. No se reconstruyen ZIP ni se publica
el repositorio como parte de una simple actualización local.

## Segundo análisis: integridad y claridad — 1.2.0

| Requisito | Implementación | Evidencia / límite |
| --- | --- | --- |
| PS-01 · Versiones | Base común, modos update/variant/merge, importación solo texto y reporte de conflictos | Tests de divergencia, copia original intacta y backup; CSS/JS arbitrario requiere integración deliberada |
| PS-02 · Composición | Regiones compartidas, separación mínima, contención real en elipse | Negativos de texto fuera de círculo y componentes cercanos sin superponerse |
| PS-03 · Densidad | Prioridades, presupuesto por rol y mapa original/ejecutivo | Revisión editorial; no compresión automática de copy |
| PS-04 · Cifras | Módulo opcional de dependencias, significado, unidades, período y fuentes | Cero/NaN/unidades/ciclos; cálculos vinculados y guardado/reapertura |
| PS-05 · Runtime | Modal aísla atajos y devuelve foco; targets sin modal fallan | Regresión real de teclado, navegación, edición y temas |
| PS-06 · Detalles | Resumen primero, supuestos después; viewport y scroll interno | Inspección de estados de modal en escritorio/teléfono |
| PS-07 · Contraste | Contraste sobre fondo efectivo simple; reglas semánticas por superficie | Pintura compleja explícitamente no medida; revisión visual pendiente |
| PS-08 · Diagramas | Actores, relaciones y mensaje antes de escoger representación | Juicio visual/editorial; no barras decorativas como falsa explicación |
| PS-09 · Voz | Copy de audiencia separado de notas; términos aprobados y reservas visibles | Anotaciones de contenido crítico/interno + revisión humana de significado |
| PS-10 · QA | Criterios separados, estados renderizados y límites; evidencia por hash | Evidencia vieja o sin observaciones editoriales no permite entrega |

Se añadieron regresiones a partir del tipo de fallo, sin reutilizar presentaciones
confidenciales ni fijar su estética como estándar. Las mejoras previas de 1.1.0 se
conservan. Los nuevos módulos son originales y opcionales cuando corresponde.

El contraste de texto es un bloqueo de entrega: 4.5:1 normal y 3:1 grande, sobre
la superficie local real, no según el nombre del tema. La regresión cubre oscuro
sobre oscuro, claro sobre blanco, acentos en anchors invertidos, spans internos,
texto sin anotación, SVG, transparencias y estados hover/focus. Los fondos complejos
no reciben un pase automático; cada slide necesita una observación de contraste.
