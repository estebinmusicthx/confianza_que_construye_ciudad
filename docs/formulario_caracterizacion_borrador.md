# Formulario de caracterización y formulación del problema — borrador

## Sección 1 – Información general del equipo

**1. Nombre del equipo:**  
[Completar]

**2. Nombre completo de los integrantes:**  
[Completar]

**3. Rol y perfil de cada integrante:**  
- Analista de datos: [Completar]
- Analista de política pública: [Completar]
- Experto/a temático o territorial: [Completar]

**4. Entidad u organización:**  
[Completar]

**5. Correo electrónico líder:**  
[Completar]

## Sección 2 – Formulación del problema

**6. Problema público a abordar:**  
Bogotá dispone de información pública sobre aporte voluntario, cumplimiento tributario, condiciones sociales y proyectos territoriales. Sin embargo, esta información permanece fragmentada entre entidades y fuentes, lo que dificulta comprender, desde la perspectiva de la ciudadanía, qué condiciones territoriales pueden fortalecer la confianza y la corresponsabilidad alrededor del aporte voluntario. Como resultado, las estrategias para promover el aporte voluntario tienden a centrarse en el recaudo y no suficientemente en la transparencia, el reconocimiento ciudadano y las condiciones territoriales que pueden favorecer una cultura tributaria más cercana.

**7. Justificación del problema:**  
El problema es relevante porque el aporte voluntario no es solo una decisión económica: es un gesto de confianza. Si la ciudadanía no encuentra una explicación clara, visible y verificable sobre el sentido público de aportar, se debilita la oportunidad de convertir el aporte voluntario en una práctica de corresponsabilidad. Analizar este fenómeno con datos abiertos permite orientar estrategias diferenciadas de pedagogía tributaria, reconocimiento y rendición de cuentas, fortaleciendo la relación entre ciudadanía y administración pública.

**8. Delimitación del análisis:**  
Ámbito territorial: Bogotá D.C., con análisis por localidad cuando las fuentes lo permiten.  
Ámbito sectorial: hacienda pública, gobierno abierto, participación ciudadana y planeación territorial.  
Población/unidad de análisis: localidades, estratos y registros administrativos agregados de predial/aporte voluntario.  
Temporalidad: aporte voluntario predial 2006-2023; cumplimiento predial 2007-2023; Encuesta Multipropósito 2021; presupuestos participativos con corte disponible en 2026.

**9. Pregunta de análisis:**  
¿Qué características territoriales se asocian con mejores condiciones para fortalecer la cultura del aporte voluntario en Bogotá y cómo pueden los datos abiertos orientar estrategias diferenciadas de transparencia, pedagogía y reconocimiento ciudadano?

**10. Hipótesis o expectativa analítica preliminar:**  
Las localidades con mejores condiciones territoriales de confianza, participación, percepción positiva del entorno y calidad de vida presentan un entorno más favorable para fortalecer estrategias de cultura tributaria y corresponsabilidad ciudadana. Estas condiciones pueden asociarse con mejores indicadores territoriales de cumplimiento predial y menor morosidad, sin que ello implique causalidad sobre el comportamiento individual de aporte voluntario.

## Sección 3 – Datos y fuentes

**11. Fuentes de datos identificadas:**  
- Recaudo Aporte Voluntario Impuesto Predial 2006-2023 — Secretaría Distrital de Hacienda.
- Cumplimiento Impuesto Predial 2007-2023 — Secretaría Distrital de Hacienda.
- Encuesta Multipropósito 2021 y Variables Adicionales EM2021 — Secretaría Distrital de Planeación.
- Presupuestos Participativos Bogotá D.C. — Secretaría Distrital de Planeación.
- Nota oficial de reconocimiento con tarjeta conmemorativa Metro — Portal Bogotá / Secretaría Distrital de Hacienda.

**12. Enlaces a los datasets:**  
Ver `docs/fuentes_y_rutas.md`.

**13. Variables clave identificadas:**  
- Aporte voluntario: año, estrato, número de contribuyentes, valor aportado.
- Cumplimiento predial: localidad, predios obligados, pagos oportunos, pagos extemporáneos, morosos, total pagado.
- Encuesta Multipropósito: variables de condiciones sociales, participación, percepción, calidad de vida o proxies disponibles.
- Presupuestos participativos: localidad, sector, proyecto, propuesta, estado, población beneficiada, presupuesto comprometido.

**14. Posible estrategia de integración:**  
La integración se realiza por nivel territorial y temporal. El aporte voluntario se analiza por año y estrato porque no incluye localidad pública. El cumplimiento predial, la Encuesta Multipropósito y presupuestos participativos se integran por localidad. La llave principal para el diagnóstico territorial es localidad; la llave temporal se usa para análisis de evolución cuando las ventanas de datos son compatibles.

**15. Información geográfica/territorial:**  
☒ Sí  ☐ No  ☐ Parcialmente  
El análisis incorpora localidad como unidad territorial principal y reconoce las limitaciones de las fuentes sin representación espacial directa.

**16. Principal entidad, sector o temática:**  
Hacienda pública, gobierno abierto, transparencia, participación ciudadana y gestión pública territorial.

## Sección 4 – Enfoque técnico y analítico

**17. ¿Incorpora género, inclusión o poblaciones diferenciales?**  
☐ Sí  ☐ No  ☒ En evaluación  
Se recomienda incorporar variables diferenciales de la Encuesta Multipropósito si la base completa se procesa con suficiente tiempo y calidad. En el diseño de política pública se propone pedagogía diferenciada por condiciones territoriales.

**18. Herramientas a utilizar:**  
☒ Python  ☐ R  ☐ Power BI  ☐ Excel  ☐ QGIS  ☐ Tableau  ☒ Looker Studio  ☒ Otro: Plotly HTML / Google Colab / GitHub.

**19. Tipo de análisis:**  
☒ Análisis exploratorio  ☒ Construcción de indicadores  ☒ Modelos estadísticos  ☒ Visualización de datos  ☐ Modelos de IA  ☒ Análisis geoespacial/territorial  ☒ Otro: matriz de decisión pública.

## Sección 5 – Experiencia con el Portal

**20. Uso previo del portal:**  
[Completar]

**21. Nivel de facilidad de uso:**  
[Completar]

**22. Principales dificultades:**  
- Fuentes con diferentes niveles de granularidad.
- Datasets con ventanas temporales no siempre equivalentes.
- Ausencia de llave territorial en el aporte voluntario.
- Archivos grandes o formatos que pueden requerir procesamiento técnico.

**23. Aspectos a mejorar:**  
- Publicar agregaciones territoriales anonimizadas del aporte voluntario.
- Mejorar diccionarios de datos y metadatos para variables de percepción/participación.
- Facilitar rutas de descarga estables y APIs para todos los recursos.
- Publicar relaciones entre recaudo, programas, proyectos y resultados cuando sea metodológicamente válido.

**24. Elementos que facilitaron el uso:**  
- Portal centralizado.
- Licencias abiertas.
- Recursos CSV/ODS.
- Diccionarios de datos en varias fuentes.

## Sección 6 – Pertinencia y aplicabilidad

Los resultados permiten orientar estrategias territoriales de cultura tributaria, transparencia y reconocimiento ciudadano. El ITCC y los cuadrantes de decisión ayudan a identificar dónde conviene priorizar reconocimiento, comunicación de beneficios, pedagogía o transparencia. La propuesta es aplicable para Secretaría de Hacienda, Planeación, Gobierno Abierto y Alcaldías Locales.

## Sección 7 – Observaciones del ejercicio

**25. Principal reto técnico o metodológico:**  
Evitar inferencias causales no sustentadas y construir una integración territorial válida a pesar de que el aporte voluntario no cuenta con llave pública por localidad.

**26. Qué hace falta para desarrollar mejor el análisis:**  
- Aporte voluntario agregado por localidad o UPL preservando privacidad.
- Metadatos más detallados sobre destinación o sectores asociados al aporte voluntario.
- Variables de confianza/percepción territorial listas para agregación.
- Llaves más homogéneas entre fuentes.

**27. Comentarios adicionales:**  
El ejercicio demuestra que los datos abiertos no solo sirven para observar la ciudad, sino para reconstruir confianza pública cuando se convierten en explicaciones claras para la ciudadanía.
