import uuid
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = "cambia-esta-clave-por-una-propia"

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
:root{--bg:#eceaff;--panel:#fff;--ink:#1e1b4b;--muted:#5f5c8c;--line:#d6d2f6;--acc:#5b3df5;--err:#c4264f;--ok:#12805c;--glass:rgba(91,61,245,.08);--edge:#8d83e6}
@media(prefers-color-scheme:dark){:root{--bg:#12102e;--panel:#1c1946;--ink:#f1efff;--muted:#a9a6d6;--line:#34306f;--acc:#8b78ff;--err:#ff7a9c;--ok:#4fdcaa;--glass:rgba(139,120,255,.1);--edge:#6a60c9}}
*{box-sizing:border-box}
body{margin:0;padding:28px 20px 48px;color:var(--ink);font-family:"Trebuchet MS","Segoe UI",system-ui,sans-serif;line-height:1.45;
background:radial-gradient(900px 420px at 85% -10%,rgba(91,61,245,.2),transparent),var(--bg)}
.wrap{max-width:1120px;margin:0 auto}
h1{margin:0 0 6px;font-size:clamp(1.9rem,4.5vw,2.8rem);font-weight:800;letter-spacing:-.02em}
.intro{max-width:62ch;margin:0 0 26px;color:var(--muted);font-size:1.05rem}
.intro b{color:var(--ink)}
.layout{display:grid;grid-template-columns:minmax(300px,400px) 1fr;gap:24px;align-items:start}
.panel{background:var(--panel);border:2px solid var(--line);border-radius:18px;padding:18px 20px;margin-bottom:16px;transition:border-color .3s,opacity .3s}
.panel.active{border-color:var(--acc)}
.panel.locked{opacity:.5}
.panel h2{display:flex;align-items:center;gap:10px;margin:0 0 6px;font-size:1.05rem}
.panel h2 i{display:grid;place-items:center;width:26px;height:26px;border-radius:50%;background:var(--acc);color:#fff;font-style:normal;font-size:.85rem}
.help{margin:0 0 8px;color:var(--muted);font-size:.9rem}
label{display:block;margin:10px 0 4px;font-size:.85rem;font-weight:700;color:var(--muted)}
input{width:100%;padding:10px 12px;border:2px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);font:inherit}
input:focus{border-color:var(--acc)}
:focus-visible{outline:3px solid var(--acc);outline-offset:2px}
button{width:100%;margin-top:12px;padding:11px 12px;border:0;border-radius:12px;color:#fff;font:inherit;font-weight:700;cursor:pointer;box-shadow:0 4px 0 rgba(0,0,0,.25);transition:transform .12s,box-shadow .12s,filter .15s}
button:hover:not(:disabled){filter:brightness(1.1);transform:translateY(-2px)}
button:active:not(:disabled){transform:translateY(3px);box-shadow:0 1px 0 rgba(0,0,0,.25)}
button:disabled{opacity:.4;cursor:not-allowed;box-shadow:none}
button small{display:block;font-weight:400;font-size:.72rem;opacity:.9}
.b-set{background:var(--ink);color:var(--panel)}.b-push{background:#5b3df5}.b-pop{background:#d6336c}.b-peek{background:#1479b5}.b-clear{background:#5d5a8a}
.ops{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.ops button{margin-top:6px}

.coach{display:flex;flex-direction:column;gap:2px;padding:14px 18px;margin-bottom:20px;min-height:84px;background:var(--panel);border:2px solid var(--line);border-left:8px solid var(--acc);border-radius:14px}
.coach b{font-size:1.1rem}.coach span{color:var(--muted)}
.coach.ok{border-left-color:var(--ok)}.coach.err{border-left-color:var(--err)}
.coach.flash{animation:flash .5s ease-out}
.board{display:grid;grid-template-columns:minmax(0,360px) 1fr;gap:28px;align-items:start}
.tube{position:relative;min-height:420px;padding:14px;display:flex;flex-direction:column;border:5px solid var(--edge);border-top:0;border-radius:0 0 30px 30px;background:linear-gradient(90deg,var(--glass),transparent 28%,transparent 72%,var(--glass))}
.stack{display:flex;flex-direction:column-reverse;gap:8px;margin-top:auto}
.item{--c:#4cc9f0;--t:#14123a;padding:10px 14px;border-radius:12px;background:var(--c);color:var(--t);box-shadow:0 4px 0 rgba(0,0,0,.2);transform-origin:bottom center}
.k1{--c:#7b6cff;--t:#fff}.k2{--c:#2ec4a0}.k3{--c:#ffc233}.k4{--c:#ff7aa8}
.item.top{outline:3px solid var(--ink);outline-offset:3px}
.hd{display:flex;justify-content:space-between;align-items:center;font-size:.75rem;font-weight:700;opacity:.85}
.badge{padding:1px 9px;border-radius:99px;background:var(--t);color:var(--c)}
.kvs{display:flex;flex-wrap:wrap;gap:4px 18px;margin-top:4px}
.kv small{display:block;font-size:.7rem;opacity:.75}.kv b{font-size:1rem;overflow-wrap:anywhere}
.ghost{padding:14px;border:2px dashed var(--edge);border-radius:12px;text-align:center;font-size:.9rem;color:var(--muted)}
.ghost.full{border-color:var(--err);color:var(--err);font-weight:700}
.drop{animation:drop .75s cubic-bezier(.4,0,.6,1)}
.pop-in{animation:popin .5s cubic-bezier(.2,1.5,.5,1)}
.side .box{padding:14px 16px;margin-bottom:16px;background:var(--panel);border:2px solid var(--line);border-radius:16px}
.side h3{margin:0 0 8px;font-size:.95rem}
.count{display:flex;justify-content:space-between;align-items:baseline;font-size:1.6rem;font-weight:800}
.count small{font-size:.85rem;font-weight:400;color:var(--muted)}
.segs{display:flex;gap:3px;margin:8px 0}.seg{flex:1;height:12px;border-radius:4px;background:var(--line);transition:background .3s}
.slot{display:grid;place-items:center;min-height:96px;padding:8px;border:2px dashed var(--edge);border-radius:12px;color:var(--muted);font-size:.9rem;text-align:center}
.slot .item{width:100%;text-align:left}
.log{margin:0;padding:0;list-style:none;max-height:180px;overflow-y:auto;font-size:.88rem}
.log li{padding:5px 0;border-bottom:1px solid var(--line);color:var(--muted)}.log li:first-child{color:var(--ink);font-weight:700}
.log:empty::after{content:"Todavía no hiciste ninguna operación.";color:var(--muted)}

@keyframes drop{0%{transform:translateY(-340px) scale(.96,1.08);opacity:0}45%{opacity:1}60%{transform:none}72%{transform:scale(1.05,.88)}86%{transform:scale(.98,1.04)}100%{transform:none}}
@keyframes popin{from{transform:scale(.5) rotate(8deg);opacity:0}to{transform:none;opacity:1}}
@keyframes flash{from{transform:translateY(-8px);opacity:.3}to{transform:none;opacity:1}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media(max-width:860px){.layout,.board{grid-template-columns:1fr}.tube{min-height:320px}}
</style>
</head>
<body>
<div class="wrap">
<h1>Simulador de pilas</h1>
<p class="intro">Una pila es como un tubo de fichas: solo podés agregar o sacar desde <b>arriba</b>. Lo último que entra es lo primero que sale. A eso se le llama <b>LIFO</b>.</p>

<div class="layout">
<div>
  <section class="panel active" id="s1">
    <h2><i>1</i> Elegí qué guarda cada elemento</h2>
    <p class="help">Escribí los nombres de los datos, separados por comas. Ejemplo: nombre, edad, carrera</p>
    <label for="camposInput">Campos</label>
    <input id="camposInput" placeholder="nombre, edad, carrera" autocomplete="off">
    <label for="capInput">Capacidad máxima (1 a 20)</label>
    <input id="capInput" type="number" min="1" max="20" value="6">
    <button class="b-set" id="btnSet">Guardar estructura</button>
  </section>

  <section class="panel locked" id="s2">
    <h2><i>2</i> Apilá un elemento</h2>
    <p class="help">Completá todos los campos y tocá Push. El elemento cae arriba de la pila.</p>
    <div id="dynamicInputs"></div>
    <button class="b-push" id="btnPush">Push<small>agrega arriba</small></button>
  </section>

  <section class="panel locked" id="s3">
    <h2><i>3</i> Probá las operaciones</h2>
    <div class="ops">
      <button class="b-pop" id="btnPop">Pop<small>saca el de arriba</small></button>
      <button class="b-peek" id="btnPeek">Peek<small>mira sin sacar</small></button>
      <button class="b-clear" id="btnClear">Clear<small>vacía todo</small></button>
    </div>
  </section>
</div>

<section>
  <div class="coach" id="coach" role="status" aria-live="polite"><b id="coachTitle"></b><span id="coachText"></span></div>
  <div class="board">
    <div class="tube" id="tube"><div class="stack" id="stackVisual"></div></div>
    <div class="side">
      <div class="box">
        <h3>Espacio usado</h3>
        <div class="count"><span id="count">0 / 6</span><small id="statState">vacía</small></div>
        <div class="segs" id="segs"></div>
      </div>
      <div class="box">
        <h3>Último elemento sacado</h3>
        <div class="slot" id="outSlot"></div>
      </div>
      <div class="box">
        <h3>Registro</h3>
        <ul class="log" id="log"></ul>
      </div>
    </div>
  </div>
</section>
</div>
</div>

<script>
const $ = id => document.getElementById(id);
const PAL = ['#4cc9f0', '#7b6cff', '#2ec4a0', '#ffc233', '#ff7aa8'];
const REDUCE = matchMedia('(prefers-reduced-motion: reduce)').matches;
const SHAKE = [{transform:'translateX(0)'},{transform:'translateX(-12px)'},{transform:'translateX(12px)'},{transform:'translateX(-7px)'},{transform:'translateX(7px)'},{transform:'translateX(0)'}];
let state = { estructura: [], capacidad: 6, pila: [] };
let busy = false;

async function api(url, method = 'POST', body = null) {
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

const resumen = obj => Object.values(obj).join(', ');

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
  Object.entries(item).forEach(([k, v]) => {
    const kv = document.createElement('div');
    kv.className = 'kv';
    const a = document.createElement('small');
    a.textContent = k;
    const b = document.createElement('b');
    b.textContent = v;
    kv.append(a, b);
    kvs.appendChild(kv);
  });
  d.append(hd, kvs);
  return d;
}

function buildInputs() {
  const box = $('dynamicInputs');
  box.innerHTML = '';
  if (!state.estructura.length) {
    const p = document.createElement('p');
    p.className = 'help';
    p.textContent = 'Primero guardá una estructura en el paso 1.';
    box.appendChild(p);
    return;
  }
  state.estructura.forEach((campo, i) => {
    const lab = document.createElement('label');
    lab.htmlFor = 'campo_' + i;
    lab.textContent = campo;
    const inp = document.createElement('input');
    inp.id = 'campo_' + i;
    inp.autocomplete = 'off';
    inp.addEventListener('keydown', e => {
      if (e.key !== 'Enter') return;
      const next = $('campo_' + (i + 1));
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
  $('statState').textContent = !p.length ? 'vacía' : full ? 'llena' : 'con elementos';

  $('btnPush').disabled = $('btnPop').disabled = $('btnPeek').disabled = $('btnClear').disabled = !has;
  $('s1').classList.toggle('active', !has);
  ['s2', 's3'].forEach(id => { $(id).classList.toggle('locked', !has); $(id).classList.toggle('active', has); });
}

function sync(data, drop = false) {
  state = { estructura: data.estructura, capacidad: data.capacidad, pila: data.pila };
  renderStack(drop);
}

function resetOut() { $('outSlot').textContent = 'Todavía no sacaste nada'; }

async function setStructure() {
  if (busy) return;
  const campos = $('camposInput').value.split(',').map(s => s.trim()).filter(Boolean);
  const data = await api('/set_structure', 'POST', { campos, capacidad: $('capInput').value });
  if (data.error) return fail(data.error);
  sync(data);
  buildInputs();
  resetOut();
  log('Estructura: ' + data.estructura.join(', ') + ' (capacidad ' + data.capacidad + ')');
  coach('ok', 'Estructura lista',
    'Cada elemento tendrá: ' + data.estructura.join(', ') + '. Caben hasta ' + data.capacidad + '. Ahora hacé Push para apilar el primero.');
  $('campo_0').focus();
}

async function pushItem() {
  if (busy || !state.estructura.length) return;
  if (state.pila.length >= state.capacidad) return fail('Overflow');
  const elemento = {};
  for (let i = 0; i < state.estructura.length; i++) {
    const val = $('campo_' + i).value.trim();
    if (!val) { $('campo_' + i).focus(); return fail('Completá el campo «' + state.estructura[i] + '».'); }
    elemento[state.estructura[i]] = val;
  }
  const data = await api('/push', 'POST', { elemento });
  if (data.error) return fail(data.error);
  sync(data, true);
  log('Push → ' + resumen(data.pushed));
  coach('ok', 'Push: entró por arriba',
    'El elemento cayó sobre la cima anterior y ahora él es la nueva cima: será el primero en salir.');
  state.estructura.forEach((_, i) => $('campo_' + i).value = '');
  $('campo_0').focus();
}

async function popItem() {
  if (busy || !state.estructura.length) return;
  const data = await api('/pop');
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
      { transform: 'translateY(-70px) rotate(-3deg)', offset: .3 },
      { transform: 'translate(' + dx + 'px,' + dy + 'px) rotate(8deg) scale(.55)', opacity: .15 }
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
  const data = await api('/peek', 'GET');
  if (data.error) return fail(data.error);
  busy = true;
  coach('', 'Peek: solo mirás', 'La cima es: ' + resumen(data.cima) + '. La pila no cambia, nada se saca.');
  const rest = { transform: 'none', boxShadow: '0 4px 0 rgba(0,0,0,.2)' };
  const up = { transform: 'translateY(-24px) scale(1.06)', boxShadow: '0 20px 30px rgba(91,61,245,.5)' };
  await anim($('stackVisual').querySelector('.top'),
    [rest, { ...up, offset: .35 }, { ...up, offset: .7 }, rest], { duration: 1200, easing: 'ease-in-out' });
  log('Peek: ' + resumen(data.cima));
  busy = false;
}

async function clearStack() {
  if (busy || !state.estructura.length) return;
  const data = await api('/clear');
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

$('btnSet').addEventListener('click', setStructure);
$('btnPush').addEventListener('click', pushItem);
$('btnPop').addEventListener('click', popItem);
$('btnPeek').addEventListener('click', peekItem);
$('btnClear').addEventListener('click', clearStack);
$('camposInput').addEventListener('keydown', e => { if (e.key === 'Enter') setStructure(); });

(async function init() {
  resetOut();
  const data = await api('/state', 'GET');
  if (!data.error) {
    sync(data);
    $('capInput').value = data.capacidad;
    $('camposInput').value = data.estructura.join(', ');
  }
  buildInputs();
  renderStack();
  coach('', data.estructura && data.estructura.length ? 'Seguimos donde lo dejaste' : 'Empecemos',
    data.estructura && data.estructura.length ? 'Tu pila sigue acá. Probá Push, Pop o Peek.' : 'Definí los campos en el paso 1 y guardá la estructura.');
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