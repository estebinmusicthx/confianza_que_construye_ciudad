# Nota técnica sobre integración de datos públicos

**Proyecto:** Confianza que Construye Ciudad  
**Propósito:** integrar fuentes públicas para orientar estrategias territoriales de cultura tributaria, transparencia y reconocimiento ciudadano.

## Fuentes integradas
Se utilizaron fuentes del Portal de Datos Abiertos Bogotá sobre aporte voluntario predial, cumplimiento predial, Encuesta Multipropósito 2021 / variables adicionales y presupuestos participativos. También se incluye una fuente documental oficial de contexto sobre la tarjeta conmemorativa del Metro para contribuyentes con aporte voluntario.

## Integración técnica
La integración se realiza por tres niveles:
1. Temporal: evolución del aporte voluntario por año.
2. Socioeconómico/estrato: aporte voluntario y condiciones de contribución por estrato.
3. Territorial: cumplimiento predial, condiciones EM y proyectos por localidad.

## Limitaciones
- El dataset de aporte voluntario predial no incluye localidad; por tanto, no se cruza territorialmente ni se atribuye a proyectos.
- Los proyectos de presupuestos participativos no son presentados como destino directo del aporte voluntario.
- El ITCC no mide causalidad ni comportamiento individual; resume condiciones territoriales observables.
- Las fuentes tienen diferentes cortes temporales.

## Recomendaciones
1. Publicar una llave territorial o agregación local del aporte voluntario preservando privacidad.
2. Crear metadatos que indiquen claramente destinación, programa o sector asociado al aporte.
3. Mantener un índice público de condiciones territoriales para corresponsabilidad.
4. Desarrollar un visor ciudadano que explique aporte, proyectos, límites y avances con lenguaje sencillo.
