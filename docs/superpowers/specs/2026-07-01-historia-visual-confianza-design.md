# Historia visual "Confianza que Construye Ciudad" — Diseño

**Fecha:** 2026-07-01
**Evento:** DATAJAM 2 — Bogotá, Dirección de Innovación Pública y Estado Abierto

## Objetivo

Convertir el dashboard existente (`index.html`, 8 gráficas Plotly generadas por
`scripts/run_analysis.py`) en una **única página de scrollytelling** que cuente la
historia del proyecto: de la idea fuerza a la recomendación de política pública,
tejiendo la narrativa del README con las visualizaciones rediseñadas.

## Decisiones aprobadas

- **Gráficas:** reconstruidas desde cero con Plotly.js 2.30 a partir de los CSV en
  `outputs/clean/`, con identidad visual uniforme (opción A).
- **Formato:** scrollytelling editorial de una sola página con reveal al hacer scroll.
- **Entrega:** reemplaza `index.html`; el original se respalda como
  `index_dashboard_original.html`.
- **Identidad:** paleta tipo Alcaldía Mayor de Bogotá, protagonismo del rojo
  (`#E4002B`), acento amarillo (`#FFCC00`), tinta `#1A1A1A`, marfil `#F7F5F2`.
- **Logos obligatorios** (reutilizados desde el base64 del original, sin pérdida):
  Datos para la transparencia, DATAJAM Edición 2, franja institucional
  (Javeriana · Escuela Javeriana de Gobierno y Ética Pública · Observatorio de
  Gobierno y TIC · ideca) y Bogotá Mi Ciudad Mi Casa.

## Arquitectura técnica

- Un solo `index.html` autocontenido (GitHub Pages).
- Plotly.js 2.30 vía CDN.
- Datos incrustados como JSON en un `<script>` final (compacto, generado de los CSV).
- Reveal con IntersectionObserver (sin librerías extra) + barra de progreso de scroll.
- Generado de forma reproducible por `scripts/build_story.py`.

## Hilo narrativo (secciones)

0. Hero — "Una ciudad no se construye solo con impuestos. Se construye con confianza." + KPIs + logos.
1. El problema — información pública fragmentada.
2. La pregunta analítica.
3. El aporte voluntario ya existe (serie 2006–2023) — línea.
4. Pedagogía diferenciada: aporte por estrato — barras.
5. El ITCC por localidad — barras horizontales.
6. Territorio tributario: morosidad por localidad — barras.
7. Modelo de decisión: 4 cuadrantes / 4 estrategias — dispersión ITCC vs morosidad.
8. Rigor: brechas de trazabilidad y lo que no se afirma — tarjetas.
9. Recomendación: programa de 5 líneas + franja institucional (footer).

## Cuidado metodológico (obligatorio en la narrativa)

- No se atribuye aporte voluntario a proyectos ni localidades.
- No se afirma causalidad entre confianza y pago.
- El ITCC es experimental, territorial y no mide comportamiento individual.
- Cada gráfica lleva reseña estratégica + fuente.

## Fuera de alcance (YAGNI)

- No se modifica el notebook ni `run_analysis.py`.
- No se agrega mapa geográfico real (los CSV no traen geometría).
- No se cambian datos ni conclusiones.
