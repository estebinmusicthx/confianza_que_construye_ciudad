# Guía rápida para montar el visor en Looker Studio

## Tablas limpias sugeridas
Subir a Google Sheets o conectar como CSV:

- `outputs/clean/itcc_localidad.csv`
- `outputs/clean/cuadrantes_decision_publica.csv`
- `outputs/clean/cumplimiento_predial_localidad.csv`
- `outputs/clean/aporte_voluntario_anual.csv`
- `outputs/clean/aporte_voluntario_estrato.csv`
- `outputs/clean/brechas_trazabilidad.csv`
- `outputs/clean/fuentes_datos_manifest.csv`

## Páginas sugeridas

### Página 1 — La pregunta ciudadana
Mensaje central: “Una ciudad no se construye únicamente con impuestos. Se construye con confianza.”
Tarjetas: aporte acumulado, contribuyentes acumulados, localidades analizadas, fuente principal.

### Página 2 — ITCC por localidad
Fuente: `itcc_localidad.csv`.
Visual: barra horizontal o mapa si se incorpora shape de localidades.
Reseña: el índice no clasifica localidades como buenas o malas; identifica condiciones territoriales para orientar pedagogía, reconocimiento y transparencia.

### Página 3 — Cuadrantes de decisión pública
Fuente: `cuadrantes_decision_publica.csv`.
Visual: dispersión ITCC vs tasa de pago oportuno.
Dimensión: localidad. Color: cuadrante.
Reseña: la innovación es pasar de una campaña genérica a estrategias territoriales diferenciadas.

### Página 4 — Aporte voluntario
Fuentes: `aporte_voluntario_anual.csv` y `aporte_voluntario_estrato.csv`.
Visuales: línea temporal y barras por estrato.
Reseña: el aporte voluntario se analiza por año y estrato; no se territorializa porque la fuente pública no trae localidad.

### Página 5 — Cumplimiento y morosidad
Fuente: `cumplimiento_predial_localidad.csv`.
Visuales: morosidad por localidad, pago oportuno, predios obligados.
Reseña: la morosidad no se presenta como juicio sobre territorios; se interpreta como señal para mejorar pedagogía, transparencia y facilidad de comprensión.

### Página 6 — Brechas y recomendaciones
Fuente: `brechas_trazabilidad.csv`.
Visual: tabla.
Reseña: una propuesta rigurosa no oculta límites; los convierte en agenda pública de mejora de datos abiertos.

## Estilo recomendado
- Título principal: “Confianza que Construye Ciudad”.
- Subtítulo: “Cómo los datos abiertos pueden fortalecer la cultura tributaria mediante transparencia, reconocimiento ciudadano y evidencia territorial”.
- Usar textos cortos debajo de cada gráfico.
- Cerrar con la frase: “La confianza no se decreta. La confianza se demuestra.”
