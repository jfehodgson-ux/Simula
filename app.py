import os
import uuid
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-de-desarrollo")

MAX_CAMPOS = 10
MAX_CAPACIDAD = 20
CAPACIDAD_DEFECTO = 8
MAX_LARGO_VALOR = 100

# Cada visitante tiene su propia pila, identificada por una cookie de sesión.
sesiones = {}


def estado():
    sid = session.get("sid")
    if sid not in sesiones:
        sid = uuid.uuid4().hex
        session["sid"] = sid
        sesiones[sid] = {"campos": [], "capacidad": CAPACIDAD_DEFECTO, "pila": []}
    return sesiones[sid]


def respuesta(s, **extra):
    return jsonify({
        "status": "success",
        "estructura": s["campos"],
        "capacidad": s["capacidad"],
        "pila": s["pila"],
        "tamano": len(s["pila"]),
        **extra,
    })


def error(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


PAGINA = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Simulador de Pilas</title>
<style>
:root{--bg:#121026;--p:#1f1b3d;--p2:#2a2550;--line:#3b3570;--acc:#6c5ce7;--muted:#a5a1c9;--ink:#f1efff;--ok:#2ee6b6;--err:#ff6b81}
*{box-sizing:border-box}
body{margin:0;padding:24px 20px 40px;display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start;color:var(--ink);font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;line-height:1.45;
background:radial-gradient(800px 380px at 80% -8%,rgba(108,92,231,.28),transparent),var(--bg)}
.top{flex:1 1 100%}
h1{margin:0 0 4px;font-size:clamp(1.7rem,4vw,2.4rem);letter-spacing:-.02em}
.sub{margin:0;color:var(--muted)}
.coach{flex:1 1 100%;display:flex;flex-direction:column;padding:14px 18px;min-height:78px;background:var(--p);border:1px solid var(--line);border-left:8px solid var(--acc);border-radius:14px}
.coach b{font-size:1.1rem}.coach span{color:var(--muted)}
.coach.ok{border-left-color:var(--ok)}.coach.err{border-left-color:var(--err)}
.coach.flash{animation:flash .5s ease-out}
.panel{flex:1;min-width:290px;background:var(--p);padding:24px;border-radius:16px;border:1px solid var(--line);transition:border-color .3s,opacity .3s,box-shadow .3s}
.panel.active{border-color:var(--acc);box-shadow:0 10px 40px rgba(108,92,231,.2)}
.panel.locked{opacity:.55}
h2{margin:0 0 6px;font-size:1.15rem;display:flex;align-items:center;gap:10px}
.step{display:grid;place-items:center;flex-shrink:0;width:28px;height:28px;border-radius:50%;background:var(--acc);color:#fff;font-size:.9rem}
.hint{margin:0 0 12px;color:var(--muted);font-size:.9rem}
label{display:block;margin:14px 0 4px;font-size:.88rem;font-weight:700;color:var(--muted)}
input{width:100%;padding:12px;background:#131127;border:1px solid var(--line);border-radius:8px;color:#fff;font:inherit;transition:border-color .2s,box-shadow .2s}
input:focus{outline:none;border-color:var(--acc);box-shadow:0 0 0 3px rgba(108,92,231,.3)}
button{width:100%;margin-top:14px;padding:12px;border:0;border-radius:10px;font:inherit;font-weight:700;cursor:pointer;box-shadow:0 4px 0 rgba(0,0,0,.35);transition:transform .12s,box-shadow .12s,filter .15s}
button:hover:not(:disabled){filter:brightness(1.12);transform:translateY(-2px)}
button:active:not(:disabled){transform:translateY(3px);box-shadow:0 1px 0 rgba(0,0,0,.35)}
button:disabled{opacity:.4;cursor:not-allowed;box-shadow:none}
button small{display:block;font-weight:400;font-size:.72rem;opacity:.85}
.b-main{background:#e0e0ff;color:#121026}.b-push{background:var(--acc);color:#fff}
.b-add{background:transparent;border:1px dashed var(--acc);color:#a99dff;width:auto;padding:8px 16px;margin-top:2px;font-size:.9rem;box-shadow:none}
.def-box{display:flex;gap:10px;align-items:center;margin-bottom:10px;padding:10px;background:var(--p2);border:1px solid #4a47a3;border-radius:10px;animation:slidein .3s ease-out}
.def-box input{border:0}
.x{width:auto;margin:0;padding:10px 14px;background:#ff4757;color:#fff;box-shadow:none}
.ops{display:flex;gap:10px;flex-wrap:wrap}.ops button{flex:1;min-width:90px;margin-top:0}
#dynamicInputs{margin-bottom:6px;padding:4px 16px 14px;background:var(--p2);border-radius:10px}
hr{border:0;border-top:1px solid var(--line);margin:26px 0}
.meter{display:flex;justify-content:space-between;align-items:baseline;font-weight:700}
.segs{display:flex;gap:3px;margin:8px 0 16px}.seg{flex:1;height:10px;border-radius:4px;background:var(--line);transition:background .3s}
.tray{display:grid;place-items:center;min-height:86px;padding:8px;border:2px dashed var(--line);border-radius:12px;color:var(--muted);font-size:.88rem;text-align:center}
.tray .item{width:100%;text-align:left}
.cap{margin:14px 0 0;font-size:.78rem;color:var(--muted);text-align:center}
.tube{max-width:300px;min-height:380px;margin:6px auto 0;padding:12px;display:flex;flex-direction:column;border:4px solid #4a47a3;border-top:0;border-radius:0 0 22px 22px;background:linear-gradient(90deg,rgba(108,92,231,.12),transparent 30%,transparent 70%,rgba(108,92,231,.12))}
.stack{display:flex;flex-direction:column-reverse;gap:8px;margin-top:auto}
.item{--c:#6c5ce7;--t:#fff;padding:10px 14px;border-radius:10px;background:var(--c);color:var(--t);box-shadow:0 4px 0 rgba(0,0,0,.3);transform-origin:bottom center}
.k1{--c:#00cec9;--t:#0b1a20}.k2{--c:#fd79a8;--t:#2a0a18}.k3{--c:#feca57;--t:#2a1e00}.k4{--c:#54a0ff;--t:#061a33}
.item.top{outline:3px solid #fff;outline-offset:3px}
.hd{display:flex;justify-content:space-between;align-items:center;font-size:.72rem;font-weight:700;opacity:.85}
.badge{padding:1px 9px;border-radius:99px;background:var(--t);color:var(--c)}
.kvs{display:flex;flex-wrap:wrap;gap:4px 18px;margin-top:4px}
.kv small{display:block;font-size:.68rem;opacity:.75}.kv b{overflow-wrap:anywhere}
.ghost{padding:12px;border:2px dashed #4a47a3;border-radius:10px;text-align:center;font-size:.88rem;color:var(--muted)}
.ghost.full{border-color:var(--err);color:var(--err);font-weight:700}
.drop{animation:drop .75s cubic-bezier(.4,0,.6,1)}
.pop-in{animation:popin .5s cubic-bezier(.2,1.5,.5,1)}
.log{margin:0;padding:0;list-style:none;max-height:130px;overflow-y:auto;font-size:.85rem}
.log li{padding:4px 0;border-bottom:1px solid var(--line);color:var(--muted)}.log li:first-child{color:var(--ink);font-weight:700}
.log:empty::after{content:"Sin operaciones todavía.";color:var(--muted)}
@keyframes drop{0%{transform:translateY(-340px) scale(.96,1.08);opacity:0}45%{opacity:1}60%{transform:none}72%{transform:scale(1.05,.88)}86%{transform:scale(.98,1.04)}100%{transform:none}}
@keyframes popin{from{transform:scale(.5) rotate(8deg);opacity:0}to{transform:none;opacity:1}}
@keyframes flash{from{transform:translateY(-8px);opacity:.3}to{transform:none;opacity:1}}
@keyframes slidein{from{transform:translateX(-24px);opacity:0}to{transform:none;opacity:1}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<div class="top">
  <h1>Simulador de pilas</h1>
  <p class="sub">LIFO: el último elemento que entra es el primero que sale. Todo pasa por la cima.</p>
</div>
<div class="coach" id="coach" role="status" aria-live="polite"><b id="coachTitle"></b><span id="coachText"></span></div>

<section class="panel active" id="s1">
  <h2><span class="step">1</span> Estructura de la Pila</h2>
  <p class="hint">Creá un recuadro por cada dato que quieras guardar.</p>
  <div id="defFieldsContainer"></div>
  <button class="b-add" id="btnAdd">+ Agregar otro campo</button>
  <label for="capacidadInput">Capacidad máxima de la pila (1 a 20)</label>
  <input type="number" id="capacidadInput" min="1" max="20" value="8">
  <button class="b-main" id="btnSet">Guardar estructura</button>
</section>

<section class="panel locked" id="s2">
  <h2><span class="step">2</span> Apilá un elemento</h2>
  <p class="hint">Completá los datos y tocá Push para meterlo a la pila.</p>
  <div id="dynamicInputs"></div>
  <button class="b-push" id="btnPush" disabled>Push (Apilar)<small>agrega arriba</small></button>
  <hr>
  <h2><span class="step">3</span> Controles de Pila</h2>
  <div class="ops">
    <button id="btnPop" style="background:#ff4757;color:#fff">Pop<small>saca el de arriba</small></button>
    <button id="btnPeek" style="background:#00d2d3;color:#121026">Peek<small>mira sin sacar</small></button>
    <button id="btnClear" style="background:#feca57;color:#121026">Clear<small>vacía todo</small></button>
  </div>
</section>

<section class="panel" style="text-align:center">
  <h2 style="justify-content:center">Pila Gráfica</h2>
  <div class="meter"><span>Capacidad</span><span id="count">0 / 8</span></div>
  <div class="segs" id="segs"></div>
  <p class="cap" style="margin:0 0 6px">Último sacado con Pop</p>
  <div class="tray" id="outSlot"></div>
  <div class="tube" id="tube"><div class="stack" id="stackVisual"></div></div>
  <h2 style="justify-content:center;margin-top:24px;font-size:1rem">Registro</h2>
  <ul class="log" id="log" style="text-align:left"></ul>
</section>

<script>
const $ = id => document.getElementById(id);
const PAL = ['#6c5ce7', '#00cec9', '#fd79a8', '#feca57', '#54a0ff'];
const REDUCE = matchMedia('(prefers-reduced-motion: reduce)').matches;
const SHAKE = [{transform:'translateX(0)'},{transform:'translateX(-12px)'},{transform:'translateX(12px)'},{transform:'translateX(-7px)'},{transform:'translateX(7px)'},{transform:'translateX(0)'}];
let state = { estructura: [], capacidad: 8, pila: [] };
let busy = false;

async function req(url, method = 'POST', body = null) {
  try {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    return await (await fetch(url, opts)).json();
  } catch (e) {
    return { error: 'No se pudo conectar con el servidor.' };
  }
}

function anim(el, kf, opt) {
  if (REDUCE || !el) return Promise.resolve();
  return el.animate(kf, opt).finished.catch(() => {});
}

function coach(kind, title, text) {
  const c = $('coach');
  c.className = 'coach ' + kind;
  $('coachTitle').textContent = title;
  $('coachText').textContent = text;
  void c.offsetWidth;
  c.classList.add('flash');
}

function log(text) {
  const li = document.createElement('li');
  li.textContent = text;
  $('log').prepend(li);
  while ($('log').children.length > 30) $('log').lastChild.remove();
}

function fail(msg) {
  const o = msg.includes('Overflow');
  const u = msg.includes('Underflow') || msg.includes('vacía');
  coach('err',
    o ? 'Overflow: la pila está llena' : u ? 'Underflow: la pila está vacía' : 'Revisá los datos',
    o ? 'No cabe nada más. Hacé Pop para liberar un lugar y volvé a probar el Push.'
      : u ? 'No hay nada que sacar. Hacé Push para apilar un elemento primero.' : msg);
  if (o || u) anim($('tube'), SHAKE, { duration: 450 });
}

// El servidor puede devolver los campos en otro orden: usamos el de la estructura.
const resumen = obj => state.estructura.map(k => obj[k]).join(', ');

function card(item, i, top) {
  const d = document.createElement('div');
  d.className = 'item k' + (i % 5) + (top ? ' top' : '');
  const hd = document.createElement('div');
  hd.className = 'hd';
  const s = document.createElement('span');
  s.textContent = 'Posición ' + i;
  hd.appendChild(s);
  if (top) {
    const b = document.createElement('span');
    b.className = 'badge';
    b.textContent = 'CIMA';
    hd.appendChild(b);
  }
  const kvs = document.createElement('div');
  kvs.className = 'kvs';
  state.estructura.forEach(k => {
    const kv = document.createElement('div');
    kv.className = 'kv';
    const a = document.createElement('small');
    a.textContent = k;
    const b = document.createElement('b');
    b.textContent = item[k];
    kv.append(a, b);
    kvs.appendChild(kv);
  });
  d.append(hd, kvs);
  return d;
}

function makeRow(value = '', removable = true) {
  const row = document.createElement('div');
  row.className = 'def-box';
  const inp = document.createElement('input');
  inp.type = 'text';
  inp.className = 'def-campo';
  inp.placeholder = 'Ej: Nombre';
  inp.autocomplete = 'off';
  inp.value = value;
  inp.addEventListener('keydown', e => { if (e.key === 'Enter') setStructure(); });
  row.appendChild(inp);
  if (removable) {
    const x = document.createElement('button');
    x.className = 'x';
    x.textContent = 'X';
    x.addEventListener('click', () => {
      anim(row, [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'translateX(30px)' }], { duration: 200 }).then(() => row.remove());
    });
    row.appendChild(x);
  }
  return row;
}

function addDefField() {
  const box = $('defFieldsContainer');
  if (box.children.length >= 10) return coach('err', 'Máximo 10 campos', 'Ya no caben más datos en cada elemento.');
  const row = makeRow('', true);
  box.appendChild(row);
  row.firstChild.focus();
}

function buildInputs() {
  const box = $('dynamicInputs');
  box.innerHTML = '';
  if (!state.estructura.length) {
    const p = document.createElement('p');
    p.className = 'hint';
    p.style.cssText = 'color:#ff8a9a;text-align:center;margin:14px 0 0';
    p.textContent = 'Primero guardá la estructura en el paso 1.';
    box.appendChild(p);
    return;
  }
  state.estructura.forEach((campo, i) => {
    const lab = document.createElement('label');
    lab.htmlFor = 'val_' + i;
    lab.textContent = campo;
    const inp = document.createElement('input');
    inp.type = 'text';
    inp.id = 'val_' + i;
    inp.autocomplete = 'off';
    inp.placeholder = 'Escribí el valor para ' + campo;
    inp.addEventListener('keydown', e => {
      if (e.key !== 'Enter') return;
      const next = $('val_' + (i + 1));
      next ? next.focus() : pushItem();
    });
    box.append(lab, inp);
  });
}

function renderStack(drop = false) {
  const c = $('stackVisual'), p = state.pila, cap = state.capacidad;
  const has = state.estructura.length > 0, full = p.length >= cap;
  c.innerHTML = '';
  p.forEach((it, i) => {
    const d = card(it, i, i === p.length - 1);
    if (drop && i === p.length - 1) d.classList.add('drop');
    c.appendChild(d);
  });
  const g = document.createElement('div');
  g.className = 'ghost' + (full ? ' full' : '');
  g.textContent = !has ? 'Definí la estructura para empezar'
    : full ? 'Pila llena: no entra nada más'
    : p.length ? 'Aquí entra el próximo elemento'
    : 'Pila vacía: el primer Push cae aquí';
  c.appendChild(g);

  $('segs').innerHTML = '';
  for (let i = 0; i < cap; i++) {
    const s = document.createElement('div');
    s.className = 'seg';
    if (i < p.length) s.style.background = PAL[i % 5];
    $('segs').appendChild(s);
  }
  $('count').textContent = p.length + ' / ' + cap;
  ['btnPush', 'btnPop', 'btnPeek', 'btnClear'].forEach(id => { $(id).disabled = !has; });
  $('s1').classList.toggle('active', !has);
  $('s2').classList.toggle('locked', !has);
  $('s2').classList.toggle('active', has);
}

function sync(data, drop = false) {
  state = { estructura: data.estructura, capacidad: data.capacidad, pila: data.pila };
  renderStack(drop);
}

function resetOut() { $('outSlot').textContent = 'Todavía no sacaste nada'; }

async function setStructure() {
  if (busy) return;
  const campos = Array.from(document.querySelectorAll('.def-campo')).map(i => i.value.trim()).filter(Boolean);
  if (!campos.length) return fail('Agregá al menos un campo con nombre.');
  const data = await req('/set_structure', 'POST', { campos, capacidad: $('capacidadInput').value });
  if (data.error) return fail(data.error);
  sync(data);
  buildInputs();
  resetOut();
  log('Estructura: ' + data.estructura.join(', ') + ' (capacidad ' + data.capacidad + ')');
  coach('ok', 'Estructura lista',
    'Cada elemento tendrá: ' + data.estructura.join(', ') + '. Caben hasta ' + data.capacidad + '. Ahora hacé Push para apilar el primero.');
  $('val_0').focus();
}

async function pushItem() {
  if (busy || !state.estructura.length) return;
  if (state.pila.length >= state.capacidad) return fail('Overflow');
  const elemento = {};
  for (let i = 0; i < state.estructura.length; i++) {
    const val = $('val_' + i).value.trim();
    if (!val) { $('val_' + i).focus(); return fail('Completá el campo «' + state.estructura[i] + '».'); }
    elemento[state.estructura[i]] = val;
  }
  const data = await req('/push', 'POST', { elemento });
  if (data.error) return fail(data.error);
  sync(data, true);
  log('Push → ' + resumen(data.pushed));
  coach('ok', 'Push: entró por arriba',
    'El elemento cayó sobre la cima anterior y ahora él es la nueva cima: será el primero en salir.');
  state.estructura.forEach((_, i) => { $('val_' + i).value = ''; });
  $('val_0').focus();
}

async function popItem() {
  if (busy || !state.estructura.length) return;
  const data = await req('/pop');
  if (data.error) return fail(data.error);
  busy = true;
  coach('ok', 'Pop: salió el de arriba',
    'Se sacó el último que entró (LIFO). La cima pasa al elemento que estaba justo debajo.');
  const top = $('stackVisual').querySelector('.top');
  if (top && !REDUCE) {
    const r = top.getBoundingClientRect(), s = $('outSlot').getBoundingClientRect();
    const dx = s.left + s.width / 2 - (r.left + r.width / 2);
    const dy = s.top + s.height / 2 - (r.top + r.height / 2);
    await anim(top, [
      { transform: 'none', opacity: 1 },
      { transform: 'translateY(40px) scale(.97)', offset: .2 },
      { transform: 'translate(' + dx + 'px,' + dy + 'px) rotate(8deg) scale(.6)', opacity: .15 }
    ], { duration: 850, easing: 'ease-in-out', fill: 'forwards' });
  }
  sync(data);
  const d = card(data.popped, data.pila.length, false);
  d.classList.add('pop-in');
  $('outSlot').innerHTML = '';
  $('outSlot').appendChild(d);
  log('Pop ← ' + resumen(data.popped));
  busy = false;
}

async function peekItem() {
  if (busy || !state.estructura.length) return;
  const data = await req('/peek', 'GET');
  if (data.error) return fail(data.error);
  busy = true;
  coach('', 'Peek: solo mirás', 'La cima es: ' + resumen(data.cima) + '. La pila no cambia, nada se saca.');
  const rest = { transform: 'none', boxShadow: '0 4px 0 rgba(0,0,0,.3)' };
  const up = { transform: 'translateY(-24px) scale(1.06)', boxShadow: '0 20px 30px rgba(0,206,201,.5)' };
  await anim($('stackVisual').querySelector('.top'),
    [rest, { ...up, offset: .35 }, { ...up, offset: .7 }, rest], { duration: 1200, easing: 'ease-in-out' });
  log('Peek: ' + resumen(data.cima));
  busy = false;
}

async function clearStack() {
  if (busy || !state.estructura.length) return;
  const data = await req('/clear');
  if (data.error) return fail(data.error);
  if (!data.eliminados) return coach('', 'Ya estaba vacía', 'No había nada que descartar.');
  busy = true;
  coach('ok', 'Clear: pila vacía', 'Se descartaron ' + data.eliminados + ' elementos de una sola vez.');
  const cards = [...$('stackVisual').querySelectorAll('.item')].reverse();
  await Promise.all(cards.map((el, i) => anim(el, [
    { transform: 'none', opacity: 1 },
    { transform: 'translateY(70px) rotate(' + (i % 2 ? -9 : 9) + 'deg)', opacity: 0 }
  ], { duration: 450, delay: i * 80, easing: 'ease-in', fill: 'forwards' })));
  sync(data);
  log('Clear: ' + data.eliminados + ' elemento(s)');
  busy = false;
}

$('btnAdd').addEventListener('click', addDefField);
$('btnSet').addEventListener('click', setStructure);
$('btnPush').addEventListener('click', pushItem);
$('btnPop').addEventListener('click', popItem);
$('btnPeek').addEventListener('click', peekItem);
$('btnClear').addEventListener('click', clearStack);

(async function init() {
  resetOut();
  const data = await req('/state', 'GET');
  const box = $('defFieldsContainer');
  if (!data.error && data.estructura.length) {
    sync(data);
    $('capacidadInput').value = data.capacidad;
    data.estructura.forEach((c, i) => box.appendChild(makeRow(c, i > 0)));
    coach('', 'Seguimos donde lo dejaste', 'Tu pila sigue acá. Probá Push, Pop o Peek.');
  } else {
    box.appendChild(makeRow('', false));
    coach('', 'Empecemos', 'Escribí los datos que va a tener cada elemento y guardá la estructura.');
  }
  buildInputs();
  renderStack();
})();
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return PAGINA


@app.route("/state", methods=["GET"])
def get_state():
    return respuesta(estado())


@app.route("/set_structure", methods=["POST"])
def set_structure():
    s = estado()
    data = request.get_json(silent=True) or {}

    campos = [str(c).strip() for c in data.get("campos", []) if str(c).strip()]
    if not campos:
        return error("Ingresá al menos un campo.")
    if len(campos) > MAX_CAMPOS:
        return error(f"Máximo {MAX_CAMPOS} campos por elemento.")

    vistos = set()
    for c in campos:
        if c.lower() in vistos:
            return error(f"El campo «{c}» está repetido.")
        vistos.add(c.lower())

    try:
        capacidad = int(data.get("capacidad", CAPACIDAD_DEFECTO))
    except (TypeError, ValueError):
        return error("La capacidad debe ser un número entero.")
    if not 1 <= capacidad <= MAX_CAPACIDAD:
        return error(f"La capacidad debe estar entre 1 y {MAX_CAPACIDAD}.")

    s["campos"] = campos
    s["capacidad"] = capacidad
    s["pila"] = []  # Cambiar la estructura reinicia la pila
    return respuesta(s)


@app.route("/push", methods=["POST"])
def push():
    s = estado()
    if not s["campos"]:
        return error("Definí la estructura primero.")
    if len(s["pila"]) >= s["capacidad"]:
        return error(f"Pila llena (Overflow): la capacidad es {s['capacidad']}.")

    elemento = (request.get_json(silent=True) or {}).get("elemento")
    if not isinstance(elemento, dict):
        return error("Faltan datos para agregar a la pila.")

    limpio = {}
    for campo in s["campos"]:
        valor = str(elemento.get(campo, "")).strip()
        if not valor:
            return error(f"Completá el campo «{campo}».")
        limpio[campo] = valor[:MAX_LARGO_VALOR]

    s["pila"].append(limpio)
    return respuesta(s, pushed=limpio)


@app.route("/pop", methods=["POST"])
def pop():
    s = estado()
    if not s["pila"]:
        return error("La pila está vacía (Underflow).")
    sacado = s["pila"].pop()
    return respuesta(s, popped=sacado)


@app.route("/peek", methods=["GET"])
def peek():
    s = estado()
    if not s["pila"]:
        return error("La pila está vacía, no hay cima que ver.")
    return respuesta(s, cima=s["pila"][-1])


@app.route("/clear", methods=["POST"])
def clear():
    s = estado()
    cantidad = len(s["pila"])
    s["pila"] = []
    return respuesta(s, eliminados=cantidad)


if __name__ == "__main__":
    app.run(debug=True)
