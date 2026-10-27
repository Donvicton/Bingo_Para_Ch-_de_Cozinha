import json
import random
from pathlib import Path

import streamlit as st

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

def desfazer():
    if ss.ordem:
        ss.ordem.pop()

def reiniciar():
    ss.ordem = []

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
    if len(ordem) == primeira:
        st.balloons()

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
