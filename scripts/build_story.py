# -*- coding: utf-8 -*-
"""
build_story.py
Genera la historia visual (scrollytelling) `index.html` de
"Confianza que Construye Ciudad" - DATAJAM 2.

- Lee los CSV limpios de outputs/clean/ y kpis.json.
- Reutiliza los 4 logos institucionales (base64) del respaldo
  index_dashboard_original.html.
- Reconstruye las graficas con Plotly.js 2.30 e identidad visual roja Bogota.

Uso:  python scripts/build_story.py
"""
import csv
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN = os.path.join(ROOT, "outputs", "clean")
BACKUP = os.path.join(ROOT, "index_dashboard_original.html")
OUT = os.path.join(ROOT, "index.html")


def read_csv(name):
    with open(os.path.join(CLEAN, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- datos
kpis = json.load(open(os.path.join(ROOT, "outputs", "kpis.json"), encoding="utf-8"))

anual = [
    {"ano": int(r["ANO_PRESENTACION"]),
     "contrib": int(float(r["contribuyentes"])),
     "valor": num(r["valor_aporte"])}
    for r in read_csv("aporte_voluntario_anual.csv")
]

est_rows = read_csv("aporte_voluntario_estrato.csv")
anio_max = max(int(r["ANO_PRESENTACION"]) for r in est_rows)
estrato = []
for r in est_rows:
    if int(r["ANO_PRESENTACION"]) == anio_max and r["ESTRATO"] in {"1", "2", "3", "4", "5", "6"}:
        estrato.append({
            "estrato": "Estrato " + r["ESTRATO"],
            "prom": num(r["aporte_promedio_por_contribuyente"]),
            "contrib": int(float(r["contribuyentes"])),
        })
estrato.sort(key=lambda d: d["estrato"])
estrato_anio = anio_max

itcc = []
for r in read_csv("itcc_localidad.csv"):
    nombre = r["NOMBRE_LOCALIDAD"].strip()
    if nombre == "NO REGISTRA":
        continue
    itcc.append({
        "loc": nombre.title(),
        "itcc": round(num(r["ITCC"]), 1),
        "moros": round(num(r["tasa_morosidad"]), 1),
    })
itcc.sort(key=lambda d: d["itcc"], reverse=True)

CUAD_SHORT = ["Embajadores", "Comunicar beneficios", "Transparencia prioritaria", "Reconocimiento"]
CUAD_COLOR = {
    "Embajadores": "#E4002B",
    "Comunicar beneficios": "#F2A100",
    "Transparencia prioritaria": "#1E5FA5",
    "Reconocimiento": "#0F9D77",
}


def short_cuad(txt):
    for k in CUAD_SHORT:
        if txt.startswith(k):
            return k
    return "Transparencia prioritaria"


cuad = []
for r in read_csv("cuadrantes_decision_publica.csv"):
    nombre = r["NOMBRE_LOCALIDAD"].strip()
    if nombre == "NO REGISTRA":
        continue
    cuad.append({
        "loc": nombre.title(),
        "itcc": round(num(r["ITCC"]), 1),
        "moros": round(num(r["tasa_morosidad"]), 1),
        "grupo": short_cuad(r["cuadrante"]),
        "accion": r["accion_recomendada"].strip(),
    })

brechas = [
    {"brecha": r["brecha"], "riesgo": r["riesgo"], "respuesta": r["respuesta_metodologica"]}
    for r in read_csv("brechas_trazabilidad.csv")
]

DATA = {
    "kpis": kpis,
    "anual": anual,
    "estrato": estrato,
    "estratoAnio": estrato_anio,
    "itcc": itcc,
    "cuad": cuad,
    "cuadColor": CUAD_COLOR,
    "brechas": brechas,
}

# ---------------------------------------------------------------- logos
# Los logos vienen embebidos en el respaldo. "datos" ya es transparente;
# "bogota/datajam/institucional" traen un fondo gris que quitamos para que
# se integren sobre el rojo (hero) y el gris oscuro (footer).
import base64
import io
from PIL import Image

html_src = open(BACKUP, encoding="utf-8").read()
raw = re.findall(r'data:image/[a-zA-Z]+;base64,([A-Za-z0-9+/=]+)', html_src)


def _load(i):
    return Image.open(io.BytesIO(base64.b64decode(raw[i]))).convert("RGBA")


def _to_uri(im):
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def knockout_white(im):
    """Convierte todo el trazo del logo a blanco (para fondo de color)."""
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a > 10:
                px[x, y] = (255, 255, 255, a)
    return im


def strip_gray(im):
    """Hace transparente el fondo gris/oliva neutro incrustado."""
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            mx, mn = max(r, g, b), min(r, g, b)
            if a > 0 and 38 <= mn and mx <= 102 and (mx - mn) <= 26:
                px[x, y] = (r, g, b, 0)
    return im


LOGO_DATOS = _to_uri(knockout_white(_load(0)))
LOGO_BOGOTA = _to_uri(strip_gray(_load(1)))
LOGO_DATAJAM = _to_uri(strip_gray(_load(2)))
LOGO_INST = _to_uri(strip_gray(_load(3)))

# ---------------------------------------------------------------- tarjetas
brechas_cards = "\n".join(
    f'''<article class="gap-card">
      <div class="gap-head"><span class="gap-dot"></span><h4>{b["brecha"]}</h4></div>
      <p class="gap-risk"><b>Riesgo:</b> {b["riesgo"]}</p>
      <p class="gap-ans"><b>Respuesta metodol&oacute;gica:</b> {b["respuesta"]}</p>
    </article>'''
    for b in brechas
)

lineas = [
    ("Trazabilidad ciudadana", "Mostrar de forma abierta cómo se usa el recaudo y el aporte."),
    ("Reconocimiento inteligente", "Agradecer y visibilizar a quienes aportan y cumplen."),
    ("Pedagogía diferenciada", "Un mensaje distinto por territorio y por estrato, no una campaña genérica."),
    ("Actualización del ITCC", "Recalcular el índice periódicamente con datos abiertos."),
    ("Gobierno abierto basado en evidencia", "Decidir con datos públicos, reproducibles y con límites declarados."),
]
lineas_cards = "\n".join(
    f'''<article class="line-card">
      <span class="line-num">{i+1}</span>
      <div><h4>{t}</h4><p>{d}</p></div>
    </article>'''
    for i, (t, d) in enumerate(lineas)
)

# ---------------------------------------------------------------- HTML
TPL = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Confianza que Construye Ciudad | DATAJAM 2</title>
<meta name="description" content="Historia de datos abiertos sobre aporte voluntario, cumplimiento predial y condiciones territoriales de confianza en Bogot&aacute;. DATAJAM 2.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
<style>
:root{
  --red:#E4002B; --red-dark:#B0001F; --coral:#EF4D66; --amber:#FFCC00;
  --ink:#1A1A1A; --paper:#F7F5F2; --paper2:#EFECE7; --card:#ffffff;
  --muted:#6b645d; --line:#E5DED5; --dark:#232320;
  --maxw:1080px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth; overflow-x:hidden}
body{
  margin:0; color:var(--ink); background:var(--paper);
  font-family:Inter,"Segoe UI",Arial,sans-serif; line-height:1.7;
  -webkit-font-smoothing:antialiased;
  overflow-x:hidden; width:100%; max-width:100%;
}
.hero,main,footer{width:100%; max-width:100%}
img{max-width:100%; display:block}
h1,h2,h3,h4{line-height:1.2; margin:0}
a{color:var(--red-dark)}

#progress{position:fixed; top:0; left:0; height:4px; width:0; background:var(--red); z-index:100; transition:width .1s linear}

.hero{position:relative; overflow:hidden; color:#fff; background:var(--red); padding:22px 6vw 68px}
.hero::after{content:""; position:absolute; right:-160px; top:-160px; width:520px; height:520px; border-radius:50%; background:var(--red-dark); opacity:.55; z-index:0}
.hero > *{position:relative; z-index:1}
.brandbar{display:flex; justify-content:space-between; align-items:center; gap:18px; max-width:var(--maxw); margin:0 auto 46px}
.logo-box{background:transparent; padding:0; box-shadow:none}
.logo-datos{height:62px} .logo-bogota{height:48px}
.hero-inner{max-width:var(--maxw); margin:0 auto}
.eyebrow{display:inline-flex; align-items:center; gap:10px; font-size:13px; font-weight:600; letter-spacing:.14em; text-transform:uppercase; color:#fff; background:rgba(0,0,0,.18); padding:8px 14px; border-radius:999px; margin-bottom:26px}
.eyebrow .tag{color:var(--amber)}
.hero h1{font-size:clamp(30px,5.4vw,58px); font-weight:800; letter-spacing:-.02em; max-width:16ch}
.hero h1 .hl{color:var(--amber)}
.hero .lead{font-size:clamp(16px,2vw,21px); max-width:60ch; margin:22px 0 0; color:#ffe3e8}
.kpis{display:grid; grid-template-columns:repeat(4,1fr); gap:16px; max-width:var(--maxw); margin:44px auto 0}
.kpi{background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.22); border-radius:16px; padding:18px 20px; backdrop-filter:blur(6px)}
.kpi b{display:block; font-size:clamp(22px,3vw,34px); font-weight:800; letter-spacing:-.01em}
.kpi span{display:block; font-size:13px; color:#ffd9df; margin-top:4px}
.datajam-strip{max-width:var(--maxw); margin:40px auto 0; display:flex; align-items:center; gap:20px; flex-wrap:wrap}
.datajam-strip img{height:88px; border-radius:12px}
.datajam-strip p{margin:0; font-size:14px; color:#ffe3e8; max-width:34ch}
.scrollcue{max-width:var(--maxw); margin:34px auto 0; font-size:13px; color:#ffd9df; display:flex; align-items:center; gap:8px}
.scrollcue .arrow{width:22px; height:22px; border-right:2px solid var(--amber); border-bottom:2px solid var(--amber); transform:rotate(45deg); animation:bob 1.6s infinite}
@keyframes bob{0%,100%{transform:translateY(0) rotate(45deg)}50%{transform:translateY(6px) rotate(45deg)}}

main{max-width:var(--maxw); margin:0 auto; padding:0 6vw}
.step{padding:74px 0; border-bottom:1px solid var(--line); opacity:0; transform:translateY(28px); transition:opacity .7s ease, transform .7s ease}
.step.in{opacity:1; transform:none}
.step:last-child{border-bottom:0}
.kicker{display:inline-flex; align-items:center; gap:10px; font-size:13px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--red-dark)}
.kicker .n{display:inline-grid; place-items:center; width:30px; height:30px; border-radius:50%; background:var(--red); color:#fff; font-size:14px}
.step h2{font-size:clamp(24px,3.6vw,40px); font-weight:800; letter-spacing:-.02em; margin:16px 0 0; max-width:22ch}
.step .prose{font-size:clamp(16px,1.5vw,18px); color:#3a3630; max-width:66ch; margin:18px 0 0}
.step .prose + .prose{margin-top:14px}

.chart-card{background:var(--card); border:1px solid var(--line); border-radius:20px; padding:20px 20px 8px; margin-top:32px; box-shadow:0 22px 50px rgba(31,20,10,.07)}
.chart-title{font-size:15px; font-weight:700; color:var(--ink); margin:0 4px 4px}
.plot{width:100%; height:440px}
.plot-tall{height:600px}
.meta{margin:14px 4px 6px; display:grid; gap:8px}
.review{font-size:14.5px; color:#2c2925; background:var(--paper2); border-left:4px solid var(--red); border-radius:0 10px 10px 0; padding:12px 16px}
.review b{color:var(--red-dark)}
.source{font-size:12.5px; color:var(--muted)}

.gap-grid{display:grid; grid-template-columns:repeat(2,1fr); gap:16px; margin-top:32px}
.gap-card{background:var(--card); border:1px solid var(--line); border-radius:16px; padding:18px 20px}
.gap-head{display:flex; align-items:flex-start; gap:10px}
.gap-dot{width:12px; height:12px; border-radius:50%; background:var(--amber); margin-top:6px; flex:none}
.gap-card h4{font-size:16px; font-weight:700}
.gap-risk{font-size:14px; color:#7a3038; margin:12px 0 0}
.gap-ans{font-size:14px; color:#3a3630; margin:8px 0 0}
.gap-risk b,.gap-ans b{font-weight:700}

.rec{background:var(--ink); color:#fff; border-radius:22px; padding:40px 34px; margin-top:34px}
.rec h3{font-size:clamp(20px,2.6vw,28px); font-weight:800}
.rec .sub{color:#c9c4bd; max-width:60ch; margin:12px 0 26px}
.line-grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px}
.line-card{display:flex; gap:14px; align-items:flex-start; background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.12); border-radius:14px; padding:16px}
.line-num{display:inline-grid; place-items:center; width:34px; height:34px; flex:none; border-radius:50%; background:var(--amber); color:var(--ink); font-weight:800}
.line-card h4{font-size:15px; font-weight:700}
.line-card p{font-size:13.5px; color:#cfc9c1; margin:5px 0 0; line-height:1.55}

.caution{display:flex; gap:14px; align-items:flex-start; background:#FFF6D8; border:1px solid #F3DE8E; border-radius:16px; padding:18px 20px; margin-top:28px}
.caution .ico{width:34px; height:34px; flex:none; border-radius:50%; background:var(--amber); color:var(--ink); font-weight:800; display:grid; place-items:center}
.caution p{margin:0; font-size:14.5px; color:#5a4a12}

footer{background:var(--dark); color:#e9e6e0; padding:56px 6vw 46px}
.foot-inner{max-width:var(--maxw); margin:0 auto}
.foot-inner h3{font-size:20px; font-weight:800}
.foot-inner p{color:#b8b3ab; font-size:14px; max-width:70ch}
.foot-logos{margin-top:28px; display:flex; gap:34px; align-items:center; flex-wrap:wrap}
.foot-logos img{height:44px; width:auto}
.foot-logos .fl-inst{height:64px}
.team{margin-top:32px; border-top:1px solid #3a3a36; padding-top:24px}
.team h4{font-size:15px; font-weight:800; color:#fff; letter-spacing:.02em}
.team h4 .rep{display:block; font-size:13px; font-weight:500; color:#b8b3ab; margin-top:4px}
.team ul{list-style:none; margin:14px 0 0; padding:0; display:grid; gap:10px}
.team li{font-size:14px; color:#d7d2ca}
.team li b{color:#fff; font-weight:700}
.team li .role{color:#a49f97}
.foot-meta{margin-top:26px; font-size:12.5px; color:#8f8a82; display:flex; justify-content:space-between; gap:16px; flex-wrap:wrap; border-top:1px solid #3a3a36; padding-top:18px}

@media(max-width:820px){
  .kpis{grid-template-columns:repeat(2,1fr)}
  .gap-grid{grid-template-columns:1fr}
  .plot{height:380px}
  .plot-tall{height:520px}
  .datajam-strip img{height:66px}
}
@media(max-width:520px){
  .kpis{grid-template-columns:1fr}
  .brandbar{flex-direction:column; align-items:flex-start}
}
</style>
</head>
<body>
<div id="progress"></div>

<header class="hero">
  <div class="brandbar">
    <div class="logo-box"><img class="logo-datos" src="__LOGO_DATOS__" alt="Datos para la transparencia"></div>
    <div class="logo-box"><img class="logo-bogota" src="__LOGO_BOGOTA__" alt="Bogot&aacute; Mi Ciudad Mi Casa"></div>
  </div>
  <div class="hero-inner">
    <span class="eyebrow"><span class="tag">DATAJAM 2</span> &middot; Datos para la transparencia</span>
    <h1>Una ciudad no se construye solo con impuestos. <span class="hl">Se construye con confianza.</span></h1>
    <p class="lead">Con datos abiertos, Bogot&aacute; puede demostrar la confianza en lugar de pedirla a ciegas. Esta es la historia del aporte voluntario, el cumplimiento predial y las condiciones territoriales que sostienen la corresponsabilidad ciudadana.</p>
  </div>
  <div class="kpis" id="kpis"></div>
  <div class="datajam-strip">
    <img src="__LOGO_DATAJAM__" alt="DATAJAM Edici&oacute;n 2 - Direcci&oacute;n de Innovaci&oacute;n P&uacute;blica y Estado Abierto">
    <p>Bogot&aacute; DataJam, Edici&oacute;n 2 &mdash; Uso y aprovechamiento de datos abiertos.</p>
  </div>
  <div class="scrollcue"><span class="arrow"></span> Baje para recorrer la historia</div>
</header>

<main>
  <section class="step">
    <span class="kicker"><span class="n">1</span> El problema</span>
    <h2>La informaci&oacute;n existe, pero est&aacute; fragmentada</h2>
    <p class="prose">Bogot&aacute; dispone de datos p&uacute;blicos sobre aporte voluntario, cumplimiento tributario, condiciones sociales y proyectos territoriales. El problema no es la falta de datos: es que est&aacute;n repartidos entre entidades y fuentes distintas.</p>
    <p class="prose">Esa fragmentaci&oacute;n dificulta comprender, desde la mirada ciudadana, qu&eacute; condiciones de un territorio fortalecen la confianza y la corresponsabilidad alrededor del aporte voluntario.</p>
  </section>

  <section class="step">
    <span class="kicker"><span class="n">2</span> La pregunta</span>
    <h2>Qu&eacute; caracter&iacute;sticas de un territorio ayudan a fortalecer la cultura del aporte</h2>
    <p class="prose">&iquest;Qu&eacute; condiciones territoriales se asocian con un mejor entorno para la cultura del aporte voluntario en Bogot&aacute;, y c&oacute;mo pueden los datos abiertos orientar estrategias diferenciadas de transparencia, pedagog&iacute;a y reconocimiento ciudadano?</p>
    <p class="prose">Para responder proponemos el <b>&Iacute;ndice Territorial de Confianza para la Corresponsabilidad (ITCC)</b>: un &iacute;ndice experimental, transparente y reproducible que resume condiciones observables de cada localidad para orientar la acci&oacute;n p&uacute;blica.</p>
  </section>

  <section class="step">
    <span class="kicker"><span class="n">3</span> La se&ntilde;al que ya existe</span>
    <h2>El aporte voluntario es una se&ntilde;al de confianza que ya se manifiesta</h2>
    <p class="prose">Entre 2006 y 2023 miles de contribuyentes aportaron de forma voluntaria en el impuesto predial. No es un fen&oacute;meno constante: sube y baja con el contexto, pero nunca desaparece. La confianza ya est&aacute; ah&iacute;, esperando ser reconocida.</p>
    <div class="chart-card">
      <p class="chart-title">Aporte voluntario anual en el impuesto predial (2006&ndash;2023)</p>
      <div id="c_anual" class="plot"></div>
      <div class="meta">
        <div class="review"><b>Rese&ntilde;a estrat&eacute;gica:</b> El aporte voluntario tiene trazabilidad en el tiempo, pero no una llave territorial p&uacute;blica. Por eso lo leemos como una se&ntilde;al agregada de confianza, sin atribuirlo a localidades ni proyectos.</div>
        <div class="source"><b>Fuente:</b> Recaudo Aporte Voluntario Impuesto Predial 2006&ndash;2023, Secretar&iacute;a Distrital de Hacienda.</div>
      </div>
    </div>
  </section>

  <section class="step">
    <span class="kicker"><span class="n">4</span> Pedagog&iacute;a diferenciada</span>
    <h2>No todos los estratos aportan igual: un solo mensaje no sirve</h2>
    <p class="prose">Cuando se mira el aporte promedio por contribuyente seg&uacute;n estrato, aparecen realidades muy distintas. Esto sugiere que la pedagog&iacute;a tributaria debe hablarle diferente a cada grupo, en lugar de repetir una campa&ntilde;a gen&eacute;rica.</p>
    <div class="chart-card">
      <p class="chart-title">Aporte voluntario promedio por contribuyente seg&uacute;n estrato (__ESTRATO_ANIO__)</p>
      <div id="c_estrato" class="plot"></div>
      <div class="meta">
        <div class="review"><b>Rese&ntilde;a estrat&eacute;gica:</b> La diferencia por estrato es de condiciones y capacidad, no un juicio sobre las personas. Orienta el tono y el contenido del mensaje, no una meta de recaudo por grupo.</div>
        <div class="source"><b>Fuente:</b> Recaudo Aporte Voluntario Impuesto Predial por estrato, Secretar&iacute;a Distrital de Hacienda.</div>
      </div>
    </div>
  </section>

  <section class="step">
    <span class="kicker"><span class="n">5</span> El &iacute;ndice</span>
    <h2>ITCC: un mapa de condiciones territoriales, no un ranking de buenos y malos</h2>
    <p class="prose">El ITCC combina cumplimiento predial y un componente social de la Encuesta Multiprop&oacute;sito 2021 para resumir, en una escala de 0 a 100, qu&eacute; tan favorables son las condiciones de cada localidad para hablar de corresponsabilidad. En esta ejecuci&oacute;n, <b>Teusaquillo</b> encabeza las condiciones territoriales.</p>
    <div class="chart-card">
      <p class="chart-title">&Iacute;ndice Territorial de Confianza para la Corresponsabilidad por localidad</p>
      <div id="c_itcc" class="plot plot-tall"></div>
      <div class="meta">
        <div class="review"><b>Rese&ntilde;a estrat&eacute;gica:</b> El gr&aacute;fico no clasifica localidades como buenas o malas. Muestra d&oacute;nde existen condiciones m&aacute;s favorables &mdash;o m&aacute;s fr&aacute;giles&mdash; para la transparencia y la pedagog&iacute;a tributaria. El ITCC no mide confianza individual.</div>
        <div class="source"><b>Fuente:</b> Construcci&oacute;n propia con Cumplimiento Impuesto Predial 2007&ndash;2023 y Encuesta Multiprop&oacute;sito 2021.</div>
      </div>
    </div>
  </section>

  <section class="step">
    <span class="kicker"><span class="n">6</span> El territorio tributario</span>
    <h2>Donde hay m&aacute;s fricci&oacute;n, debe haber m&aacute;s explicaci&oacute;n</h2>
    <p class="prose">La morosidad predial tambi&eacute;n tiene territorio. Las localidades con mayor fricci&oacute;n no son un problema a se&ntilde;alar, sino una prioridad para la trazabilidad y la pedagog&iacute;a: son las que m&aacute;s necesitan que la ciudad explique el sentido del aporte.</p>
    <div class="chart-card">
      <p class="chart-title">Tasa de morosidad predial por localidad (%)</p>
      <div id="c_moros" class="plot plot-tall"></div>
      <div class="meta">
        <div class="review"><b>Rese&ntilde;a estrat&eacute;gica:</b> Alta morosidad marca d&oacute;nde priorizar transparencia y acompa&ntilde;amiento, no d&oacute;nde castigar. La lectura es de condiciones territoriales, no de juicios sobre las personas.</div>
        <div class="source"><b>Fuente:</b> Cumplimiento Impuesto Predial 2007&ndash;2023, Secretar&iacute;a Distrital de Hacienda.</div>
      </div>
    </div>
  </section>

  <section class="step">
    <span class="kicker"><span class="n">7</span> El modelo de decisi&oacute;n</span>
    <h2>Cuatro estrategias, no una campa&ntilde;a gen&eacute;rica</h2>
    <p class="prose">Al cruzar el ITCC con la morosidad, cada localidad cae en un cuadrante que sugiere una estrategia distinta: activar embajadores, comunicar beneficios, reconocer o priorizar transparencia. As&iacute; los datos abiertos se vuelven un modelo de decisi&oacute;n para priorizar la comunicaci&oacute;n p&uacute;blica.</p>
    <div class="chart-card">
      <p class="chart-title">Modelo de decisi&oacute;n: ITCC frente a morosidad, por localidad</p>
      <div id="c_cuad" class="plot plot-tall"></div>
      <div class="meta">
        <div class="review"><b>Rese&ntilde;a estrat&eacute;gica:</b> Los cuadrantes orientan la estrategia de comunicaci&oacute;n, no destinan recursos ni predicen qui&eacute;n pagar&aacute;. Son un mapa para decidir d&oacute;nde reconocer y d&oacute;nde explicar m&aacute;s.</div>
        <div class="source"><b>Fuente:</b> Construcci&oacute;n propia (ITCC) y Cumplimiento Impuesto Predial, Secretar&iacute;a Distrital de Hacienda.</div>
      </div>
    </div>
  </section>

  <section class="step">
    <span class="kicker"><span class="n">8</span> El rigor</span>
    <h2>Lo que no podemos afirmar tambi&eacute;n importa</h2>
    <p class="prose">La honestidad metodol&oacute;gica es parte de la propuesta. Estas son las brechas de trazabilidad que reconocemos y c&oacute;mo respondemos a cada una sin forzar conclusiones.</p>
    <div class="gap-grid">
      __BRECHAS__
    </div>
    <div class="caution">
      <span class="ico">!</span>
      <p>Este an&aacute;lisis <b>no prueba</b> que una persona aporte por ver proyectos, ni afirma causalidad entre confianza y pago. Identifica condiciones territoriales y brechas para orientar mejor la pol&iacute;tica p&uacute;blica. El ITCC es experimental y reproducible.</p>
    </div>
  </section>

  <section class="step">
    <span class="kicker"><span class="n">9</span> La recomendaci&oacute;n</span>
    <h2>Programa "Confianza que Construye Ciudad"</h2>
    <p class="prose">La evidencia se traduce en una recomendaci&oacute;n concreta de pol&iacute;tica p&uacute;blica: un programa de cinco l&iacute;neas para pasar de pedir confianza a demostrarla con datos abiertos.</p>
    <div class="rec">
      <h3>Cinco l&iacute;neas de acci&oacute;n</h3>
      <p class="sub">Transparencia, reconocimiento y pedagog&iacute;a diferenciada, sostenidas por un &iacute;ndice que se actualiza y por gobierno abierto basado en evidencia.</p>
      <div class="line-grid">
        __LINEAS__
      </div>
    </div>
  </section>
</main>

<footer>
  <div class="foot-inner">
    <h3>Confianza que Construye Ciudad</h3>
    <p>Propuesta de uso y aprovechamiento de datos abiertos para fortalecer la cultura del aporte voluntario y la corresponsabilidad ciudadana en Bogot&aacute;. Presentada en DATAJAM 2.</p>
    <div class="foot-logos">
      <img src="__LOGO_DATOS__" alt="Datos para la transparencia">
      <img src="__LOGO_BOGOTA__" alt="Bogot&aacute; Mi Ciudad Mi Casa">
      <img class="fl-inst" src="__LOGO_INST__" alt="Pontificia Universidad Javeriana, Escuela Javeriana de Gobierno y &Eacute;tica P&uacute;blica, Observatorio de Gobierno y TIC, ideca">
    </div>
    <div class="team">
      <h4>Equipo: SOLUTIONSCITY <span class="rep">en representaci&oacute;n de Caja de Vivienda Popular &mdash; CVP</span></h4>
      <ul>
        <li><span class="role">Perfil t&eacute;cnico en an&aacute;lisis y visualizaci&oacute;n de datos &mdash;</span> <b>Julio Esteban Fuentes Herrera</b></li>
        <li><span class="role">Perfil de an&aacute;lisis sectorial o de pol&iacute;tica p&uacute;blica &mdash;</span> <b>Juan Carlos Sanabria Medina</b></li>
        <li><span class="role">Perfil complementario (tem&aacute;tico, metodol&oacute;gico o t&eacute;cnico) &mdash;</span> <b>Diego Fernando Guarin Marin</b></li>
      </ul>
    </div>
    <div class="foot-meta">
      <span>DATAJAM 2 &mdash; Direcci&oacute;n de Innovaci&oacute;n P&uacute;blica y Estado Abierto</span>
      <span>Fuentes: Secretar&iacute;a Distrital de Hacienda &middot; Secretar&iacute;a Distrital de Planeaci&oacute;n (EM2021)</span>
    </div>
  </div>
</footer>

<script id="data" type="application/json">__DATA_JSON__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const nf = new Intl.NumberFormat('es-CO');
const FONT = {family:"Inter, 'Segoe UI', Arial, sans-serif", color:'#1A1A1A', size:13};
const CFG = {displayModeBar:false, responsive:true};
const AX = {gridcolor:'#ECE6DD', linecolor:'#D8D2C8', zeroline:false, tickfont:{size:12}};
function base(extra){
  return Object.assign({
    font:FONT, paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
    autosize:true, margin:{t:16,r:20,b:52,l:60},
    hoverlabel:{bgcolor:'#1A1A1A', font:{color:'#fff', family:FONT.family}},
    xaxis:Object.assign({}, AX), yaxis:Object.assign({}, AX)
  }, extra||{});
}

(function(){
  const k = DATA.kpis;
  const total = DATA.anual.reduce((s,d)=>s+d.valor,0);
  const milesMillones = (total/1e9).toLocaleString('es-CO',{minimumFractionDigits:1,maximumFractionDigits:1});
  const items = [
    ['$'+milesMillones+' mil M', 'aportados voluntariamente (COP)'],
    [nf.format(k.contribuyentes_total), 'contribuyentes voluntarios'],
    [k.localidades, 'localidades analizadas'],
    [k.anio_inicio+'–'+k.anio_fin, 'serie histórica']
  ];
  document.getElementById('kpis').innerHTML = items.map(
    it=>`<div class="kpi"><b>${it[0]}</b><span>${it[1]}</span></div>`).join('');
})();

function drawAnual(){
  const x = DATA.anual.map(d=>d.ano);
  const y = DATA.anual.map(d=>d.valor/1e6);
  Plotly.newPlot('c_anual', [{
    x, y, type:'scatter', mode:'lines+markers',
    line:{color:'#E4002B', width:3.5, shape:'spline'},
    marker:{color:'#E4002B', size:7, line:{color:'#fff', width:1.5}},
    fill:'tozeroy', fillcolor:'rgba(228,0,43,0.10)',
    hovertemplate:'%{x}<br>Aporte: $%{y:,.0f} millones<extra></extra>'
  }], base({
    yaxis:Object.assign({}, AX, {title:{text:'Millones de pesos (COP)', font:{size:12}}, ticksuffix:' M'}),
    xaxis:Object.assign({}, AX, {dtick:2})
  }), CFG);
}

function drawEstrato(){
  const x = DATA.estrato.map(d=>d.estrato);
  const y = DATA.estrato.map(d=>d.prom);
  const cols = ['#F6B3C0','#EF8296','#EC5A6F','#E4002B','#C60026','#B0001F'];
  Plotly.newPlot('c_estrato', [{
    x, y, type:'bar',
    marker:{color:cols, line:{width:0}},
    hovertemplate:'%{x}<br>Promedio: $%{y:,.0f} por contribuyente<extra></extra>'
  }], base({
    yaxis:Object.assign({}, AX, {title:{text:'Aporte promedio (COP)', font:{size:12}}}),
    bargap:0.35
  }), CFG);
}

function drawItcc(){
  const arr = DATA.itcc.slice().sort((a,b)=>a.itcc-b.itcc);
  const y = arr.map(d=>d.loc);
  const x = arr.map(d=>d.itcc);
  const max = Math.max(...x), min = Math.min(...x);
  const cols = x.map(v=>{
    const t=(v-min)/(max-min||1);
    const c1=[246,179,192], c2=[228,0,43];
    const m=i=>Math.round(c1[i]+(c2[i]-c1[i])*t);
    return `rgb(${m(0)},${m(1)},${m(2)})`;
  });
  Plotly.newPlot('c_itcc', [{
    x, y, type:'bar', orientation:'h',
    marker:{color:cols, line:{width:0}},
    text:x.map(v=>v.toFixed(0)), textposition:'outside', cliponaxis:false,
    textfont:{size:11, color:'#8a1020'},
    hovertemplate:'%{y}<br>ITCC: %{x:.1f}/100<extra></extra>'
  }], base({
    margin:{t:16,r:36,b:52,l:132},
    xaxis:Object.assign({}, AX, {title:{text:'ITCC (0–100)', font:{size:12}}, range:[0,113]}),
    yaxis:Object.assign({}, AX, {automargin:true, tickfont:{size:11.5}})
  }), CFG);
}

function drawMoros(){
  const arr = DATA.itcc.slice().sort((a,b)=>a.moros-b.moros);
  const y = arr.map(d=>d.loc);
  const x = arr.map(d=>d.moros);
  const cols = x.map(v=> v>=15 ? '#B0001F' : v>=12 ? '#E4002B' : '#F2A100');
  Plotly.newPlot('c_moros', [{
    x, y, type:'bar', orientation:'h',
    marker:{color:cols, line:{width:0}},
    text:x.map(v=>v.toFixed(1)+'%'), textposition:'outside', cliponaxis:false,
    textfont:{size:11, color:'#8a1020'},
    hovertemplate:'%{y}<br>Morosidad: %{x:.1f}%<extra></extra>'
  }], base({
    margin:{t:16,r:44,b:52,l:132},
    xaxis:Object.assign({}, AX, {title:{text:'Tasa de morosidad (%)', font:{size:12}}, range:[0, Math.max(...x)+6]}),
    yaxis:Object.assign({}, AX, {automargin:true, tickfont:{size:11.5}})
  }), CFG);
}

function drawCuad(){
  const LABEL = new Set(['Teusaquillo','Sumapaz','Ciudad Bolivar','Usme','Engativa','Bosa']);
  const groups = {};
  DATA.cuad.forEach(d=>{ (groups[d.grupo]=groups[d.grupo]||[]).push(d); });
  const xs = DATA.cuad.map(d=>d.itcc), ys = DATA.cuad.map(d=>d.moros);
  const traces = Object.keys(groups).map(g=>{
    const rows = groups[g];
    return {
      x: rows.map(d=>d.itcc), y: rows.map(d=>d.moros),
      text: rows.map(d=>LABEL.has(d.loc) ? d.loc : ''),
      customdata: rows.map(d=>[d.loc, d.accion]),
      name: g, type:'scatter', mode:'markers+text',
      textposition:'top center', textfont:{size:10, color:'#4a4640'}, cliponaxis:false,
      marker:{size:13, color:DATA.cuadColor[g], line:{color:'#fff', width:1.4}},
      hovertemplate:'<b>%{customdata[0]}</b><br>ITCC: %{x:.1f} · Morosidad: %{y:.1f}%<br>%{customdata[1]}<extra>'+g+'</extra>'
    };
  });
  Plotly.newPlot('c_cuad', traces, base({
    margin:{t:28,r:24,b:74,l:62},
    legend:{orientation:'h', y:-0.17, font:{size:12}},
    xaxis:Object.assign({}, AX, {title:{text:'ITCC (condiciones territoriales) →', font:{size:12}}, range:[Math.min(...xs)-5, Math.max(...xs)+5]}),
    yaxis:Object.assign({}, AX, {title:{text:'Morosidad (fricción) →', font:{size:12}}, range:[Math.min(...ys)-2, Math.max(...ys)+4]})
  }), CFG);
}

const drawers = {c_anual:drawAnual, c_estrato:drawEstrato, c_itcc:drawItcc, c_moros:drawMoros, c_cuad:drawCuad};
const drawn = {};
const io = new IntersectionObserver((entries)=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      e.target.classList.add('in');
      e.target.querySelectorAll('.plot').forEach(p=>{
        if(!drawn[p.id] && drawers[p.id]){ drawn[p.id]=1; requestAnimationFrame(drawers[p.id]); }
      });
    }
  });
},{threshold:0.12});
document.querySelectorAll('.step').forEach(s=>io.observe(s));

const prog = document.getElementById('progress');
addEventListener('scroll', ()=>{
  const h = document.documentElement;
  const p = h.scrollTop/(h.scrollHeight-h.clientHeight);
  prog.style.width = (p*100)+'%';
}, {passive:true});

addEventListener('resize', ()=>{
  Object.keys(drawn).forEach(id=>{ const el=document.getElementById(id); if(el) Plotly.Plots.resize(el); });
});
</script>
</body>
</html>
"""

html = (TPL
        .replace("__LOGO_DATOS__", LOGO_DATOS)
        .replace("__LOGO_BOGOTA__", LOGO_BOGOTA)
        .replace("__LOGO_DATAJAM__", LOGO_DATAJAM)
        .replace("__LOGO_INST__", LOGO_INST)
        .replace("__ESTRATO_ANIO__", str(estrato_anio))
        .replace("__BRECHAS__", brechas_cards)
        .replace("__LINEAS__", lineas_cards)
        .replace("__DATA_JSON__", json.dumps(DATA, ensure_ascii=False)))

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print("OK -> index.html  (%d KB)" % (len(html.encode("utf-8")) // 1024))
print("Secciones: 9 | Graficas: 5 | Localidades ITCC: %d | Cuadrantes: %d" %
      (len(itcc), len(cuad)))
