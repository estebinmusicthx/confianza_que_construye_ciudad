# Confianza que Construye Ciudad

**Bogotá DataJam Edición 2 — Uso y aprovechamiento de datos abiertos**

## 1. Idea fuerza

Una ciudad no se construye únicamente con impuestos. Se construye con confianza.

Esta propuesta pregunta: **¿qué tanto puede explicar la ciudad a la ciudadanía sobre el sentido de aportar voluntariamente?**

No se afirma que ver proyectos cause mayor aporte voluntario. El análisis identifica condiciones territoriales observables y brechas de trazabilidad para orientar estrategias diferenciadas de transparencia, reconocimiento ciudadano y pedagogía tributaria.

## 2. Problema público

Bogotá dispone de información pública sobre aporte voluntario, cumplimiento tributario, condiciones sociales y proyectos territoriales. Sin embargo, esta información permanece fragmentada entre entidades y fuentes. Esa fragmentación dificulta comprender, desde la perspectiva ciudadana, qué condiciones territoriales pueden fortalecer la confianza y la corresponsabilidad alrededor del aporte voluntario.

## 3. Pregunta analítica

**¿Qué características territoriales se asocian con mejores condiciones para fortalecer la cultura del aporte voluntario en Bogotá y cómo pueden los datos abiertos orientar estrategias diferenciadas de transparencia, pedagogía y reconocimiento ciudadano?**

## 4. Hipótesis preliminar

Las localidades con mejores condiciones territoriales de confianza, participación, percepción positiva del entorno y calidad de vida presentan un entorno más favorable para fortalecer estrategias de cultura tributaria y corresponsabilidad ciudadana. Estas condiciones pueden asociarse con mejores indicadores territoriales de cumplimiento predial y menor morosidad, sin que ello implique causalidad sobre el comportamiento individual de aporte voluntario.

## 5. Innovación metodológica

Se propone el **Índice Territorial de Confianza para la Corresponsabilidad (ITCC)**, un índice experimental, transparente y reproducible que resume condiciones territoriales para orientar acciones públicas.

El ITCC no mide comportamiento individual ni predice quién pagará. Sirve como modelo de decisión para priorizar estrategias de comunicación y gobierno abierto.

## 6. Fuentes principales

| Fuente | Entidad | Uso |
|---|---|---|
| Recaudo Aporte Voluntario Impuesto Predial 2006-2023 | Secretaría Distrital de Hacienda | Evolución del aporte por año y estrato |
| Cumplimiento Impuesto Predial 2007-2023 | Secretaría Distrital de Hacienda | Cumplimiento, morosidad y pago oportuno por localidad |
| Encuesta Multipropósito 2021 / variables adicionales | Secretaría Distrital de Planeación | Condiciones sociales y de entorno para ITCC |
| Presupuestos Participativos Bogotá D.C. | Secretaría Distrital de Planeación | Proyectos visibles, participación y presupuesto territorial |
| Tarjeta conmemorativa Metro 2026 | Portal Bogotá / Secretaría Distrital de Hacienda | Contexto de reconocimiento ciudadano |

Ver rutas exactas en `docs/fuentes_y_rutas.md` y `outputs/clean/fuentes_datos_manifest.csv`.

## 7. Estructura del repositorio

```text
/data                  # Datasets descargados manualmente si se requiere
/notebooks             # Notebook reproducible de Colab
/scripts               # Script Python principal
/outputs               # Visualizaciones y resultados generados
/docs                  # Formulario, nota técnica, pitch, fuentes y metodología
README.md
requirements.txt
```

## 8. Cómo ejecutar

### Opción A — Google Colab

1. Abrir `notebooks/01_confianza_que_construye_ciudad.ipynb`.
2. Ejecutar la celda de instalación.
3. Ejecutar todas las celdas.
4. Descargar el ZIP de outputs.

### Opción B — Local

```bash
pip install -r requirements.txt
python scripts/run_analysis.py
```

## 9. Salidas esperadas

```text
outputs/dashboard_confianza_que_construye_ciudad.html
outputs/resumen_hallazgos.md
outputs/clean/aporte_voluntario_anual.csv
outputs/clean/aporte_voluntario_estrato.csv
outputs/clean/cumplimiento_predial_localidad.csv
outputs/clean/itcc_localidad.csv
outputs/clean/cuadrantes_decision_publica.csv
outputs/clean/brechas_trazabilidad.csv
outputs/clean/fuentes_datos_manifest.csv
```

## 10. Cuidado metodológico

- No se atribuye aporte voluntario a proyectos específicos.
- No se afirma causalidad entre confianza y pago.
- El ITCC es experimental y reproducible.
- Los hallazgos se presentan como condiciones territoriales y no como juicios sobre localidades.

## 11. Recomendación de política pública

Crear el programa **Confianza que Construye Ciudad**, compuesto por cinco líneas:

1. Trazabilidad ciudadana.
2. Reconocimiento inteligente.
3. Pedagogía diferenciada.
4. Actualización periódica del ITCC.
5. Gobierno abierto basado en evidencia.
