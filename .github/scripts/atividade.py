"""Atualiza a seção "Atividade recente" do README com os últimos commits nos repositórios públicos.

Roda todo dia pela GitHub Action .github/workflows/atividade.yml e pode rodar localmente:
    GITHUB_TOKEN=... python .github/scripts/atividade.py

Só usa a biblioteca padrão. Reescreve apenas o trecho entre os marcadores do README.
"""

import json
import os
import re
import urllib.request
from datetime import datetime
from pathlib import Path

USER = "leonardo-sferreira"
LIMITE = 5
IGNORAR = {USER.lower()}  # o próprio repositório do perfil
README = Path(__file__).resolve().parents[2] / "README.md"
INICIO, FIM = "<!-- atividade:inicio -->", "<!-- atividade:fim -->"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def api(caminho):
    req = urllib.request.Request(f"https://api.github.com{caminho}")
    req.add_header("Accept", "application/vnd.github+json")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def data_br(iso):
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return f"{d.day:02d} {MESES[d.month - 1]} {d.year}"


def linhas():
    repos = api(f"/users/{USER}/repos?type=owner&sort=pushed&per_page=30")
    saida = []
    for repo in repos:
        if repo["private"] or repo["fork"] or repo["name"].lower() in IGNORAR:
            continue
        commits = api(f"/repos/{USER}/{repo['name']}/commits?per_page=10")
        commit = next((c for c in commits if "[bot]" not in (c.get("author") or {}).get("login", "")), None)
        if not commit:
            continue
        partes = [l.strip() for l in commit["commit"]["message"].splitlines() if l.strip()]
        msg = partes[0]
        if msg.startswith("Merge pull request") and len(partes) > 1:
            msg = partes[1]  # o título do PR vem logo depois
        msg = re.sub(r"\s*\(#\d+\)$", "", msg).replace("|", "\\|")
        if len(msg) > 90:
            msg = msg[:87].rstrip() + "..."
        quando = data_br(commit["commit"]["committer"]["date"])
        saida.append(
            f"| [**{repo['name']}**]({repo['html_url']}) | [{msg}]({commit['html_url']}) | {quando} |"
        )
        if len(saida) == LIMITE:
            break
    return saida


def main():
    texto = README.read_text(encoding="utf-8")
    if INICIO not in texto or FIM not in texto:
        raise SystemExit("Marcadores de atividade não encontrados no README.")
    tabela = "\n".join(["| Repositório | Último commit | Quando |", "| --- | --- | --- |", *linhas()])
    novo = re.sub(
        re.escape(INICIO) + r".*?" + re.escape(FIM),
        f"{INICIO}\n{tabela}\n{FIM}",
        texto,
        flags=re.S,
    )
    if novo != texto:
        README.write_text(novo, encoding="utf-8")
        print("README atualizado.")
    else:
        print("Nada mudou.")


if __name__ == "__main__":
    main()
