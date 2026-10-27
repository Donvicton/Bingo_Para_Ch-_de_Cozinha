import json
import random
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# ---------- Dados ----------
BASE = Path(__file__).parent
CARTELAS = {int(k): v for k, v in json.loads((BASE / "cartelas.json").read_text(encoding="utf-8")).items()}

PALAVRAS = [
    "Panela", "Frigideira", "Prato", "Copo", "Talher", "Colher de pau", "Concha",
    "Escumadeira", "Faca", "Tábua", "Tigela", "Travessa", "Bacia", "Peneira",
    "Ralador", "Abridor de lata", "Saca rolhas", "Jarra", "Garrafa térmica", "Bule",
    "Xícara", "Pires", "Guardanapo", "Toalha de mesa", "Pano de prato", "Luva térmica",
    "Avental", "Forma de bolo", "Assadeira", "Forma de pão", "Tapete", "Lixeira",
    "Organizador", "Pote", "Porta tempero", "Saleiro", "Açucareiro",
    "Porta papel toalha", "Escorredor de louça", "Cesto de roupa",
    "Prendedor de roupa", "Cabide", "Vassoura", "Rodo", "Pá de lixo", "Balde",
    "Saboneteira", "Dispenser", "Cesto organizador", "Almofada",
]
NUM = {p: i + 1 for i, p in enumerate(PALAVRAS)}
LIVRE = "LIVRE"

MODOS = {
    "Cartela cheia": "cheia",
    "Linha, coluna ou diagonal": "linha",
}

# ---------- Lógica ----------
def linhas_da_cartela(g):
    """Todas as 12 linhas possíveis (5 horizontais, 5 verticais, 2 diagonais)."""
    rows = [g[r] for r in range(5)]
    cols = [[g[r][c] for r in range(5)] for c in range(5)]
    diags = [[g[i][i] for i in range(5)], [g[i][4 - i] for i in range(5)]]
    return rows + cols + diags


def marcada(palavra, sorteadas):
    return palavra == LIVRE or palavra in sorteadas


def faltando(g, sorteadas, modo):
    """Quantas palavras faltam para a cartela ganhar."""
    if modo == "cheia":
        return sum(1 for r in g for p in r if not marcada(p, sorteadas))
    return min(sum(1 for p in ln if not marcada(p, sorteadas)) for ln in linhas_da_cartela(g))


def rodada_da_vitoria(g, ordem, modo):
    """Em qual rodada (1-based) a cartela completou. None se ainda não."""
    s = set()
    for i, p in enumerate(ordem, start=1):
        s.add(p)
        if faltando(g, s, modo) == 0:
            return i
    return None


# ---------- Roleta de desempate ----------
def roleta_html(rol):
    html = """
<div id="box">
  <div id="titulo">🎡 Roleta do desempate</div>
  <div id="wrap"><div id="ponteiro"></div><canvas id="w"></canvas></div>
  <div id="res">&nbsp;</div>
</div>
<style>
  body{margin:0;font-family:system-ui,sans-serif;background:transparent}
  #box{background:#fbf3ea;border:2px solid #c8693f;border-radius:16px;padding:10px 0 12px;text-align:center}
  #titulo{font-weight:800;color:#4a5a2a;font-size:18px;margin-bottom:6px}
  #wrap{position:relative;width:340px;height:340px;margin:0 auto}
  #ponteiro{position:absolute;left:50%;top:-4px;transform:translateX(-50%);z-index:2;width:0;height:0;
    border-left:16px solid transparent;border-right:16px solid transparent;border-top:34px solid #222;
    filter:drop-shadow(0 2px 2px rgba(0,0,0,.4))}
  #res{font-size:28px;font-weight:800;color:#1b5e20;margin-top:8px;min-height:36px;opacity:0;transition:opacity .6s}
  #res.on{opacity:1}
</style>
<script>
const C = __CANDS__, W = __WIN__, N = __NONCE__;
const S = 340, R = S/2 - 10, n = C.length, seg = 2*Math.PI/n;
const cores = ['#e53935','#fdd835','#1e88e5','#43a047','#fb8c00','#8e24aa','#00acc1','#d81b60'];
const cv = document.getElementById('w'), ctx = cv.getContext('2d');
const dpr = window.devicePixelRatio || 1;
cv.width = S*dpr; cv.height = S*dpr; cv.style.width = S+'px'; cv.style.height = S+'px';
ctx.scale(dpr, dpr);

function cor(i){ let c = i % cores.length; if (i === n-1 && n > 1 && c === 0) c = 2; return cores[c]; }

function draw(rot, luz){
  ctx.clearRect(0,0,S,S);
  ctx.save(); ctx.translate(S/2, S/2); ctx.rotate(rot);
  for (let i=0;i<n;i++){
    const a = -Math.PI/2 + i*seg;
    ctx.beginPath(); ctx.moveTo(0,0); ctx.arc(0,0,R,a,a+seg); ctx.closePath();
    ctx.fillStyle = cor(i); ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.stroke();
    ctx.save(); ctx.rotate(a + seg/2);
    ctx.fillStyle = cor(i) === '#fdd835' ? '#333' : '#fff';
    ctx.font = 'bold ' + (n > 8 ? 18 : 24) + 'px system-ui';
    ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
    ctx.fillText(String(C[i]).padStart(2,'0'), R-18, 0);
    ctx.restore();
  }
  ctx.restore();
  // aro com lâmpadas
  ctx.save(); ctx.translate(S/2, S/2);
  ctx.beginPath(); ctx.arc(0,0,R,0,2*Math.PI); ctx.lineWidth = 8; ctx.strokeStyle = '#c8693f'; ctx.stroke();
  for (let k=0;k<24;k++){
    const t = k*2*Math.PI/24;
    ctx.beginPath(); ctx.arc(Math.cos(t)*R, Math.sin(t)*R, 4, 0, 2*Math.PI);
    ctx.fillStyle = (k + luz) % 2 ? '#fff59d' : '#fff'; ctx.fill();
  }
  ctx.beginPath(); ctx.arc(0,0,28,0,2*Math.PI); ctx.fillStyle = '#fff'; ctx.fill();
  ctx.lineWidth = 4; ctx.strokeStyle = '#c8693f'; ctx.stroke();
  ctx.fillStyle = '#c8693f'; ctx.font = '24px system-ui'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('★', 0, 1);
  ctx.restore();
}

// som de "tique" a cada fatia
let ac = null;
try { ac = new (window.AudioContext || window.webkitAudioContext)(); } catch(e) {}
function tique(){
  if (!ac) return;
  try {
    if (ac.state === 'suspended') ac.resume();
    const o = ac.createOscillator(), g = ac.createGain();
    o.type = 'square'; o.frequency.value = 900;
    g.gain.setValueAtTime(0.08, ac.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + 0.05);
    o.connect(g); g.connect(ac.destination); o.start(); o.stop(ac.currentTime + 0.05);
  } catch(e) {}
}

const alvo = (C.indexOf(W) + 0.5) * seg;
const jitter = (((N % 1000) / 1000) - 0.5) * seg * 0.6;
const fim = 2*Math.PI*8 - alvo + jitter;
const res = document.getElementById('res');
function mostrar(){ res.textContent = '🎉 Cartela ' + String(W).padStart(2,'0') + ' venceu!'; res.classList.add('on'); }

let jaGirou = false;
try { jaGirou = sessionStorage.getItem('roleta_' + N) === '1'; } catch(e) {}

if (jaGirou) { draw(fim, 0); mostrar(); }
else {
  const dur = 7000, t0 = performance.now();
  let ultima = -1;
  function frame(t){
    const p = Math.min((t - t0) / dur, 1);
    const e = 1 - Math.pow(1 - p, 4);
    const rot = fim * e;
    const fatia = Math.floor((((-rot) % (2*Math.PI)) + 2*Math.PI) % (2*Math.PI) / seg);
    if (fatia !== ultima) { tique(); ultima = fatia; }
    draw(rot, Math.floor(t / 150));
    if (p < 1) requestAnimationFrame(frame);
    else {
      mostrar();
      try { sessionStorage.setItem('roleta_' + N, '1'); } catch(e) {}
    }
  }
  requestAnimationFrame(frame);
}
</script>
"""
    return (html.replace("__CANDS__", json.dumps(rol["cands"]))
                .replace("__WIN__", str(rol["winner"]))
                .replace("__NONCE__", str(rol["nonce"])))


# ---------- Estado ----------
st.set_page_config(page_title="Bingo · Chá de Casa Nova", page_icon="🏠", layout="centered")
ss = st.session_state
ss.setdefault("ordem", [])

def sortear():
    restantes = [p for p in PALAVRAS if p not in ss.ordem]
    if restantes:
        ss.ordem.append(random.choice(restantes))

def marcar_manual():
    p = ss.get("manual")
    if p and p not in ss.ordem:
        ss.ordem.append(p)
    ss.manual = None

def limpar_desempate():
    ss.pop("roleta", None)
    ss.pop("balao", None)

def desfazer():
    if ss.ordem:
        ss.ordem.pop()
    limpar_desempate()

def reiniciar():
    ss.ordem = []
    limpar_desempate()

def girar_roleta(cands):
    ss.roleta = {"cands": list(cands), "winner": random.choice(cands),
                 "nonce": random.randint(1, 10**9)}

# ---------- CSS ----------
st.markdown("""
<style>
.atual {text-align:center; padding:18px 8px; border-radius:16px;
        background:#fbf3ea; border:2px solid #c8693f; margin:8px 0 14px;}
.atual .n {font-size:20px; color:#c8693f; font-weight:700;}
.atual .p {font-size:40px; font-weight:800; color:#4a5a2a; line-height:1.15;}
.ganhou {padding:12px; border-radius:12px; background:#e8f5e9; border:2px solid #2e7d32;
         font-size:20px; font-weight:700; color:#1b5e20; margin-bottom:8px;}
.chips {display:flex; flex-wrap:wrap; gap:5px;}
.chip {padding:4px 8px; border-radius:999px; font-size:13px; border:1px solid #d9b99a;}
.chip.on {background:#c8693f; color:#fff; border-color:#c8693f;}
.chip.off {color:#a08a78;}
table.cart {border-collapse:collapse; width:100%; table-layout:fixed;}
table.cart td {border:1px solid #c8693f; height:58px; text-align:center; font-size:12px;
               padding:2px; word-wrap:break-word;}
table.cart td.m {background:#c8693f; color:#fff; font-weight:700;}
table.cart td.l {background:#f1e1cc; color:#c8693f; font-weight:700;}
</style>
""", unsafe_allow_html=True)

# ---------- UI ----------
st.title("🏠 Bingo · Chá de Casa Nova")
st.caption("Raelle e Donivcton")

modo_label = st.radio("Como ganha?", list(MODOS), horizontal=True)
modo = MODOS[modo_label]

ordem = ss.ordem
sorteadas = set(ordem)

c1, c2, c3 = st.columns([2, 1, 1])
c1.button("🎲 Sortear", on_click=sortear, use_container_width=True, type="primary",
          disabled=len(ordem) == len(PALAVRAS))
c2.button("↩️ Desfazer", on_click=desfazer, use_container_width=True, disabled=not ordem)
c3.button("🔄 Zerar", on_click=reiniciar, use_container_width=True, disabled=not ordem)

with st.expander("Marcar palavra manualmente (sorteio em papel)"):
    st.selectbox("Palavra", [None] + [p for p in PALAVRAS if p not in sorteadas],
                 format_func=lambda p: "—" if p is None else f"{NUM[p]:02d}. {p}",
                 key="manual", on_change=marcar_manual)

if ordem:
    p = ordem[-1]
    st.markdown(f'<div class="atual"><div class="n">Rodada {len(ordem)} · Nº {NUM[p]:02d}</div>'
                f'<div class="p">{p}</div></div>', unsafe_allow_html=True)
else:
    st.info("Toque em **Sortear** para começar.")

# Vencedoras
venc = []
for n, g in CARTELAS.items():
    r = rodada_da_vitoria(g, ordem, modo)
    if r:
        venc.append((r, n))
venc.sort()

if venc:
    primeira = venc[0][0]
    primeiras = [n for r, n in venc if r == primeira]
    nums = ", ".join(f"{n:02d}" for n in primeiras)
    st.markdown(f'<div class="ganhou">🎉 BINGO! Cartela{"s" if len(primeiras) > 1 else ""} '
                f'{nums} (rodada {primeira})</div>', unsafe_allow_html=True)
    if len(venc) > len(primeiras):
        outras = ", ".join(f"{n:02d} (r{r})" for r, n in venc if r != primeira)
        st.caption(f"Também completaram depois: {outras}")
    if len(ordem) == primeira and ss.get("balao") != primeira:
        st.balloons()
        ss.balao = primeira

    # Desempate
    if len(primeiras) > 1:
        st.markdown(f"**Empate entre {len(primeiras)} cartelas!** Gire a roleta para escolher a vencedora.")
        rol = ss.get("roleta")
        if not rol or rol["cands"] != primeiras:
            st.button("🎡 Girar roleta", on_click=girar_roleta, args=(primeiras,),
                      type="primary", use_container_width=True)
        else:
            html = roleta_html(rol)
            if hasattr(st, "iframe"):          # Streamlit >= 1.52
                st.iframe(html, height=480)
            else:
                components.html(html, height=480)

# Quase lá
quase = sorted(n for n, g in CARTELAS.items() if faltando(g, sorteadas, modo) == 1)
if ordem:
    st.write(f"**Falta 1:** {', '.join(f'{n:02d}' for n in quase) if quase else '—'}")

# Palavras
st.subheader(f"Sorteadas ({len(ordem)}/{len(PALAVRAS)})")
chips = "".join(
    f'<span class="chip {"on" if p in sorteadas else "off"}">{NUM[p]:02d} {p}</span>'
    for p in PALAVRAS
)
st.markdown(f'<div class="chips">{chips}</div>', unsafe_allow_html=True)
if ordem:
    with st.expander("Ordem do sorteio"):
        st.write(" → ".join(ordem))

# Conferir cartela
st.subheader("Conferir cartela")
n = st.number_input("Número da cartela", 1, len(CARTELAS), venc[0][1] if venc else 1)
g = CARTELAS[int(n)]
rows = ""
for r in g:
    rows += "<tr>" + "".join(
        f'<td class="{"l" if p == LIVRE else "m" if p in sorteadas else ""}">'
        f'{"❤ LIVRE" if p == LIVRE else p}</td>' for p in r) + "</tr>"
st.markdown(f'<table class="cart">{rows}</table>', unsafe_allow_html=True)
f = faltando(g, sorteadas, modo)
st.write("✅ **Cartela completa!**" if f == 0 else f"Faltam **{f}** palavra(s).")
