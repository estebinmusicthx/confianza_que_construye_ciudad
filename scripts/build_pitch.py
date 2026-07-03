# -*- coding: utf-8 -*-
"""
build_pitch.py
Genera `pitch.html`: la presentacion (deck) del pitch de 3 minutos de
"Confianza que Construye Ciudad" - DATAJAM 2.

- Deck a pantalla completa, identidad roja Alcaldia de Bogota.
- Navegacion con flechas / espacio / clic; puntos de progreso.
- Reutiliza los 4 logos (transparentes) del respaldo y un QR real al sitio.
- Ultima hoja: equipo, integrantes e iconos institucionales.

Uso:  python scripts/build_pitch.py
"""
import base64
import io
import os
import re
import qrcode
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP = os.path.join(ROOT, "index_dashboard_original.html")
OUT = os.path.join(ROOT, "pitch.html")
SITE_URL = "https://estebinmusicthx.github.io/confianza_que_construye_ciudad/"

# ---------------------------------------------------------------- logos
raw = re.findall(r'data:image/[a-zA-Z]+;base64,([A-Za-z0-9+/=]+)',
                 open(BACKUP, encoding="utf-8").read())


def _load(i):
    return Image.open(io.BytesIO(base64.b64decode(raw[i]))).convert("RGBA")


def _to_uri(im):
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def knockout_white(im):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a > 10:
                px[x, y] = (255, 255, 255, a)
    return im


def strip_gray(im):
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

# ---------------------------------------------------------------- QR
qr = qrcode.QRCode(border=1, box_size=12)
qr.add_data(SITE_URL)
qr.make(fit=True)
QR_URI = _to_uri(qr.make_image(fill_color="#1A1A1A", back_color="white").convert("RGBA"))

# ---------------------------------------------------------------- HTML
TPL = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Confianza que Construye Ciudad — Pitch DATAJAM 2</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root{--red:#E4002B;--red-dark:#B0001F;--amber:#FFCC00;--ink:#141414;--paper:#F7F5F2}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:#000;font-family:Inter,"Segoe UI",Arial,sans-serif}
.deck{position:fixed;inset:0}
.slide{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;
  padding:7vmin 9vmin;opacity:0;transform:translateY(24px) scale(.995);
  transition:opacity .55s ease,transform .55s ease;pointer-events:none;color:#fff}
.slide.active{opacity:1;transform:none;pointer-events:auto}
.bg-red{background:var(--red)}
.bg-red::after{content:"";position:absolute;right:-12vmin;top:-12vmin;width:52vmin;height:52vmin;border-radius:50%;background:var(--red-dark);opacity:.5;z-index:0}
.bg-dark{background:var(--ink)}
.slide>*{position:relative;z-index:1}
.kick{font-size:2.1vmin;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:var(--amber);margin-bottom:3vmin}
.slide h1{font-size:8.4vmin;font-weight:900;line-height:1.02;letter-spacing:-.02em;max-width:20ch}
.slide h2{font-size:6.6vmin;font-weight:800;line-height:1.06;letter-spacing:-.02em;max-width:20ch}
.hl{color:var(--amber)}
.lead{font-size:2.9vmin;font-weight:400;line-height:1.5;max-width:46ch;margin-top:4vmin;color:#ffe3e8}
.huge{font-size:9.5vmin;font-weight:900;line-height:1.03;letter-spacing:-.03em;max-width:18ch}
.eye-top{position:absolute;top:6vmin;left:9vmin;right:9vmin;display:flex;justify-content:space-between;align-items:center;z-index:2}
.eye-top img{height:7vmin;width:auto}
.eye-top .l2{height:5vmin}

.chips{display:flex;gap:2vmin;flex-wrap:wrap;margin-top:5vmin}
.chip{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);border-radius:2vmin;padding:1.6vmin 2.4vmin;font-size:2.3vmin;font-weight:600}
.stat{display:flex;gap:2.4vmin;margin-top:5vmin}
.stat b{display:block;font-size:5vmin;font-weight:900;line-height:1}
.stat span{font-size:1.9vmin;color:#ffd9df}
.stat div{background:rgba(255,255,255,.1);border-radius:2vmin;padding:2vmin 2.6vmin}

.grid4{display:grid;grid-template-columns:1fr 1fr;gap:2.4vmin;margin-top:5vmin;max-width:100%}
.q{border-radius:2.2vmin;padding:3vmin 3.2vmin}
.q h3{font-size:3.1vmin;font-weight:800;margin-bottom:1vmin}
.q p{font-size:2.1vmin;line-height:1.4;opacity:.92}
.q.e{background:#E4002B;box-shadow:inset 0 0 0 .35vmin #ffffff33}
.q.c{background:#F2A100;color:#3a2500}
.q.r{background:#0F9D77}
.q.t{background:#1E5FA5}

.lines{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2vmin;margin-top:5vmin}
.ln{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:1.8vmin;padding:2.4vmin}
.ln .n{display:inline-grid;place-items:center;width:5vmin;height:5vmin;border-radius:50%;background:var(--amber);color:var(--ink);font-weight:900;font-size:2.4vmin;margin-bottom:1.4vmin}
.ln h4{font-size:2.4vmin;font-weight:700}
.ln p{font-size:1.8vmin;opacity:.85;margin-top:.6vmin;line-height:1.35}

.close-wrap{display:flex;align-items:center;gap:6vmin;justify-content:space-between}
.qr{background:#fff;padding:1.6vmin;border-radius:2vmin;flex:none}
.qr img{width:26vmin;height:26vmin;display:block}
.qr p{color:var(--ink);text-align:center;font-size:1.8vmin;font-weight:700;margin-top:1vmin}

/* creditos */
.credits h2{font-size:6vmin}
.team-name{font-size:3vmin;color:#ffd9df;margin-top:1.5vmin;font-weight:500}
.members{margin-top:5vmin;display:grid;gap:2.4vmin}
.member{display:flex;align-items:baseline;gap:2vmin;flex-wrap:wrap}
.member b{font-size:3vmin;font-weight:800;color:#fff}
.member span{font-size:2.1vmin;color:#b9b3ab}
.icons{margin-top:auto;padding-top:6vmin;display:flex;align-items:center;gap:5vmin;flex-wrap:wrap}
.icons img{height:6.5vmin;width:auto}
.icons .big{height:8.5vmin}

/* chrome */
.dots{position:fixed;bottom:3.2vmin;left:0;right:0;display:flex;justify-content:center;gap:1.4vmin;z-index:20}
.dot{width:1.3vmin;height:1.3vmin;border-radius:50%;background:#ffffff55;transition:.3s;cursor:pointer}
.dot.on{background:#fff;width:3.4vmin;border-radius:1vmin}
.count{position:fixed;bottom:3vmin;right:4vmin;color:#ffffffaa;font-size:1.8vmin;font-weight:600;z-index:20}
.hint{position:fixed;bottom:3vmin;left:4vmin;color:#ffffff88;font-size:1.6vmin;z-index:20}
@media(max-width:760px){
  .slide h1{font-size:10vmin}.grid4{grid-template-columns:1fr}.lines{grid-template-columns:1fr}
  .close-wrap{flex-direction:column;align-items:flex-start;gap:3vmin}.qr img{width:34vmin;height:34vmin}
}
</style>
</head>
<body>
<div class="deck" id="deck">

  <section class="slide bg-red active">
    <div class="eye-top">
      <img src="__DATOS__" alt="Datos para la transparencia">
      <img class="l2" src="__BOGOTA__" alt="Bogota Mi Ciudad Mi Casa">
    </div>
    <div class="kick">DATAJAM 2 · Datos para la transparencia</div>
    <h1>Una ciudad no se construye solo con impuestos. <span class="hl">Se construye con confianza.</span></h1>
    <p class="lead">Equipo SOLUTIONSCITY · Caja de Vivienda Popular (CVP)</p>
  </section>

  <section class="slide bg-red">
    <div class="kick">El problema</div>
    <h2>La información existe. Pero está rota en pedazos.</h2>
    <p class="lead">Aporte voluntario, cumplimiento predial, condiciones sociales y proyectos ciudadanos viven separados entre entidades y cortes de tiempo. El ciudadano paga… pero no ve. Y lo que no se ve, no construye confianza.</p>
  </section>

  <section class="slide bg-red">
    <div class="kick">El giro</div>
    <p class="lead" style="margin:0 0 2vmin">Dejamos de preguntar cuánto más puede aportar la gente.</p>
    <div class="huge">¿Cuánto más puede <span class="hl">explicar</span> la ciudad?</div>
  </section>

  <section class="slide bg-red">
    <div class="kick">La innovación</div>
    <h2>ITCC: un mapa de confianza, no un ranking de culpables.</h2>
    <p class="lead">El Índice Territorial de Confianza para la Corresponsabilidad mide, de 0 a 100 y con las mismas reglas para las 20 localidades, qué tan favorable es cada territorio para hablar de confianza. No juzga personas. No inventa causas. <b>Mide condiciones.</b></p>
    <div class="stat">
      <div><b>0–100</b><span>escala comparable</span></div>
      <div><b>20</b><span>localidades, mismas reglas</span></div>
      <div><b>4</b><span>fuentes públicas integradas</span></div>
    </div>
  </section>

  <section class="slide bg-red">
    <div class="kick">El modelo de decisión</div>
    <h2>No hay una Bogotá. Hay cuatro.</h2>
    <div class="grid4">
      <div class="q e"><h3>Embajadores</h3><p>Alta confianza y alto cumplimiento: activar vocerías y reconocimiento.</p></div>
      <div class="q c"><h3>Comunicar</h3><p>Buenas condiciones, menor cumplimiento: mostrar resultados y beneficios.</p></div>
      <div class="q r"><h3>Reconocer</h3><p>Cumplen, pero la confianza es frágil: agradecer y reforzar transparencia.</p></div>
      <div class="q t"><h3>Transparencia</h3><p>Más fricción: pedagogía, trazabilidad y presencia institucional.</p></div>
    </div>
  </section>

  <section class="slide bg-red">
    <div class="kick">La propuesta</div>
    <h2>Programa <span class="hl">Confianza que Construye Ciudad</span></h2>
    <div class="lines">
      <div class="ln"><span class="n">1</span><h4>Trazabilidad ciudadana</h4><p>Mostrar abiertamente cómo se usa el aporte.</p></div>
      <div class="ln"><span class="n">2</span><h4>Reconocimiento inteligente</h4><p>Del gesto (la tarjeta del Metro) a política permanente.</p></div>
      <div class="ln"><span class="n">3</span><h4>Pedagogía diferenciada</h4><p>Un mensaje por territorio, no una campaña genérica.</p></div>
      <div class="ln"><span class="n">4</span><h4>ITCC vivo</h4><p>Un índice que se actualiza con datos abiertos.</p></div>
      <div class="ln"><span class="n">5</span><h4>Gobierno abierto</h4><p>Decidir con evidencia y límites declarados.</p></div>
    </div>
  </section>

  <section class="slide bg-red">
    <div class="close-wrap">
      <div>
        <div class="kick">El cierre</div>
        <h1>La confianza no se decreta. <span class="hl">Se demuestra.</span></h1>
        <div class="stat">
          <div><b>185.485</b><span>contribuyentes</span></div>
          <div><b>$7,1 mil M</b><span>aportados (COP)</span></div>
          <div><b>20</b><span>localidades</span></div>
        </div>
      </div>
      <div class="qr"><img src="__QR__" alt="QR al sitio"><p>Explórelo →</p></div>
    </div>
  </section>

  <section class="slide bg-dark credits">
    <div class="kick">Equipo</div>
    <h2>SOLUTIONSCITY</h2>
    <p class="team-name">en representación de la Caja de Vivienda Popular — CVP</p>
    <div class="members">
      <div class="member"><b>Julio Esteban Fuentes Herrera</b><span>— Perfil técnico en análisis y visualización de datos</span></div>
      <div class="member"><b>Juan Carlos Sanabria Medina</b><span>— Perfil de análisis sectorial o de política pública</span></div>
      <div class="member"><b>Diego Armando Gonzalez Quiroga</b><span>— Perfil complementario (temático, metodológico o técnico)</span></div>
    </div>
    <div class="icons">
      <img class="big" src="__DATAJAM__" alt="DATAJAM Edición 2">
      <img src="__DATOS__" alt="Datos para la transparencia">
      <img src="__BOGOTA__" alt="Bogota Mi Ciudad Mi Casa">
      <img src="__INST__" alt="Javeriana, Escuela de Gobierno, Observatorio TIC, ideca">
    </div>
  </section>

</div>

<div class="dots" id="dots"></div>
<div class="count" id="count"></div>
<div class="hint">← → o barra espaciadora · F pantalla completa</div>

<script>
const slides=[...document.querySelectorAll('.slide')];
const dots=document.getElementById('dots');
const count=document.getElementById('count');
let i=0;
slides.forEach((_,k)=>{const d=document.createElement('div');d.className='dot';d.onclick=()=>go(k);dots.appendChild(d);});
function render(){
  slides.forEach((s,k)=>s.classList.toggle('active',k===i));
  [...dots.children].forEach((d,k)=>d.classList.toggle('on',k===i));
  count.textContent=(i+1)+' / '+slides.length;
}
function go(n){i=Math.max(0,Math.min(slides.length-1,n));render();}
function next(){go(i+1);} function prev(){go(i-1);}
addEventListener('keydown',e=>{
  if(['ArrowRight',' ','PageDown','Enter'].includes(e.key)){e.preventDefault();next();}
  else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();prev();}
  else if(e.key==='Home'){go(0);} else if(e.key==='End'){go(slides.length-1);}
  else if(e.key==='f'||e.key==='F'){toggleFS();}
});
addEventListener('click',e=>{ if(e.target.closest('.dot'))return; const x=e.clientX/innerWidth; x<0.28?prev():next(); });
function toggleFS(){ if(!document.fullscreenElement)document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen(); else document.exitFullscreen&&document.exitFullscreen(); }
render();
</script>
</body>
</html>
"""

html = (TPL.replace("__DATOS__", LOGO_DATOS)
           .replace("__BOGOTA__", LOGO_BOGOTA)
           .replace("__DATAJAM__", LOGO_DATAJAM)
           .replace("__INST__", LOGO_INST)
           .replace("__QR__", QR_URI))
open(OUT, "w", encoding="utf-8").write(html)
print("OK -> pitch.html  (%d KB)  8 diapositivas" % (len(html.encode("utf-8")) // 1024))
