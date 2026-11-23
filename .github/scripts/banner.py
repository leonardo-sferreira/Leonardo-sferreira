"""Gera assets/banner.svg: o banner animado do perfil, na identidade do portfólio.

Reproduz em SVG puro (o GitHub não roda JavaScript no README):
- a constelação do hero: partículas que se movem e linhas que surgem quando duas ficam próximas;
- o nome revelado palavra por palavra;
- o papel que alterna dentro da pílula;
- a barra de progresso no topo.

Rodar: python .github/scripts/banner.py
"""

import math
import random
from pathlib import Path

W, H = 1200, 340
BG = "#0b0d10"
TEAL = "45,212,191"
BLUE = "79,143,240"
TEXT = "#eef1f4"
MUTED = "#8993a1"
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"

N_PARTICLES = 40
KEYFRAMES = 7          # posições por ciclo (a última volta para a primeira)
CYCLE = 28             # segundos por ciclo
STEP = 70              # deslocamento máximo entre posições
LINK = 140             # distância máxima para desenhar a linha

ROLES = ["Back-end e APIs", "Banco de Dados", "Automações", "Web"]
NAME = ["Leonardo", "dos", "Santos"]

random.seed(7)


def walk():
    x, y = random.uniform(0, W), random.uniform(0, H)
    pts = [(x, y)]
    for _ in range(KEYFRAMES - 1):
        x = min(W, max(0, x + random.uniform(-STEP, STEP)))
        y = min(H, max(0, y + random.uniform(-STEP, STEP)))
        pts.append((x, y))
    pts.append(pts[0])
    return pts


def vals(seq):
    return ";".join(f"{v:.0f}" for v in seq)


particles = []
for _ in range(N_PARTICLES):
    particles.append({
        "pts": walk(),
        "r": random.uniform(1.2, 2.6),
        "c": TEAL if random.random() < 0.55 else BLUE,
    })

anim = f'dur="{CYCLE}s" repeatCount="indefinite"'

lines = []
for i in range(N_PARTICLES):
    for j in range(i + 1, N_PARTICLES):
        a, b = particles[i]["pts"], particles[j]["pts"]
        d = [math.dist(a[k], b[k]) for k in range(KEYFRAMES + 1)]
        if min(d) >= LINK:
            continue
        op = [max(0.0, 0.32 * (1 - dk / LINK)) for dk in d]
        lines.append(
            f'<line stroke="rgb({TEAL})" stroke-width="1">'
            f'<animate attributeName="x1" values="{vals(p[0] for p in a)}" {anim}/>'
            f'<animate attributeName="y1" values="{vals(p[1] for p in a)}" {anim}/>'
            f'<animate attributeName="x2" values="{vals(p[0] for p in b)}" {anim}/>'
            f'<animate attributeName="y2" values="{vals(p[1] for p in b)}" {anim}/>'
            f'<animate attributeName="stroke-opacity" values="{";".join(f"{o:.2f}".lstrip("0") or "0" for o in op)}" {anim}/>'
            f"</line>"
        )

dots = []
for p in particles:
    xs, ys = vals(q[0] for q in p["pts"]), vals(q[1] for q in p["pts"])
    dots.append(
        f'<circle r="{p["r"]:.1f}" fill="rgb({p["c"]})" fill-opacity="0.85">'
        f'<animate attributeName="cx" values="{xs}" {anim}/>'
        f'<animate attributeName="cy" values="{ys}" {anim}/>'
        f"</circle>"
    )

# Nome: sobe, aparece e é revelado da esquerda para a direita (independe da largura da fonte).
name_svg = [
    '<g class="name" clip-path="url(#nameClip)">'
    f'<text x="72" y="172" class="word">{" ".join(NAME)}</text></g>'
]

# Papel alternando: cada texto fica visível por 1/len(ROLES) do ciclo.
ROLE_CYCLE = 2.4 * len(ROLES)
role_svg = []
for i, role in enumerate(ROLES):
    role_svg.append(
        f'<text class="role" x="124" y="226" opacity="{1 if i == 0 else 0}">{role}'
        f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.04;0.21;0.25;1" '
        f'dur="{ROLE_CYCLE}s" begin="{1.1 + i * 2.4:.1f}s" repeatCount="indefinite"/></text>'
    )

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Leonardo dos Santos, desenvolvedor de software">
<title>Leonardo dos Santos · Desenvolvedor de Software</title>
<style>
  text {{ font-family: {FONT}; }}
  .eyebrow {{ fill: rgb({TEAL}); font-size: 15px; font-weight: 600; letter-spacing: 3.5px; animation: fade .7s ease .1s both; }}
  .word {{ fill: {TEXT}; font-size: 64px; font-weight: 700; letter-spacing: -1.5px; }}
  .name {{ animation: rise .9s cubic-bezier(.22,1,.36,1) .3s both; }}
  .value {{ fill: {MUTED}; font-size: 19px; animation: fade .8s ease .9s both; }}
  .pill {{ animation: fade .7s ease 1.1s both; }}
  .role {{ fill: {TEXT}; font-size: 17px; font-weight: 600; }}
  .link {{ fill: rgb({TEAL}); font-size: 15px; font-weight: 600; animation: fade .7s ease 1.3s both; }}
  .dot {{ animation: pulse 1.8s ease-in-out infinite; transform-origin: 104px 220px; }}
  @keyframes fade {{ from {{ opacity: 0; }} }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(22px); }} }}
  @keyframes pulse {{ 0%, 100% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: .45; transform: scale(.7); }} }}
  @media (prefers-reduced-motion: reduce) {{
    .eyebrow, .name, .value, .pill, .link {{ animation: none; }}
    .dot {{ animation: none; }}
  }}
</style>
<defs>
  <clipPath id="nameClip"><rect x="60" y="90" height="110" width="{W}"><animate attributeName="width" values="0;0;{W}" keyTimes="0;0.24;1" dur="1.45s" fill="freeze" calcMode="spline" keySplines="0 0 1 1;0.22 1 0.36 1"/></rect></clipPath>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <linearGradient id="fadeLeft" x1="0" x2="1" y1="0" y2="0">
    <stop offset="0" stop-color="{BG}" stop-opacity="0.96"/>
    <stop offset="0.48" stop-color="{BG}" stop-opacity="0.78"/>
    <stop offset="0.8" stop-color="{BG}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="barGrad" x1="0" x2="1"><stop offset="0" stop-color="rgb({TEAL})"/><stop offset="1" stop-color="rgb({BLUE})"/></linearGradient>
  <radialGradient id="glow" cx="0.82" cy="0.45" r="0.55">
    <stop offset="0" stop-color="rgb({TEAL})" stop-opacity="0.10"/>
    <stop offset="1" stop-color="rgb({TEAL})" stop-opacity="0"/>
  </radialGradient>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect width="{W}" height="{H}" fill="url(#glow)"/>
  <g>{"".join(lines)}</g>
  <g>{"".join(dots)}</g>
  <rect width="{W}" height="{H}" fill="url(#fadeLeft)"/>
  <rect x="0" y="0" height="3" width="0" fill="url(#barGrad)"><animate attributeName="width" values="0;{W};{W}" keyTimes="0;0.7;1" dur="6s" repeatCount="indefinite"/></rect>

  <text class="eyebrow" x="74" y="98">DESENVOLVEDOR DE SOFTWARE</text>
  {"".join(name_svg)}

  <g class="pill">
    <rect x="74" y="200" width="260" height="40" rx="20" fill="rgb({TEAL})" fill-opacity="0.08" stroke="rgb({TEAL})" stroke-opacity="0.35"/>
    <circle class="dot" cx="104" cy="220" r="5" fill="rgb({TEAL})"/>
    {"".join(role_svg)}
  </g>

  <text class="value" x="74" y="282">Construo sistemas que resolvem problemas reais, da regra de negócio ao deploy.</text>
  <text class="link" x="74" y="314">leonardo-sferreira.github.io/portfolio  →</text>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="#ffffff" stroke-opacity="0.06"/>
</g>
</svg>
"""

out = Path(__file__).resolve().parents[2] / "assets" / "banner.svg"
out.parent.mkdir(exist_ok=True)
out.write_text(svg, encoding="utf-8")
print(f"{out} · {len(svg) / 1024:.0f} KB · {len(lines)} linhas · {N_PARTICLES} partículas")
