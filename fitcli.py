"""fitcli - CLI para explorar a API wger (Workout Manager).

TP1 de ALPCD 2026/27, com os módulos requests, re e typer.

Uso:
    python fitcli.py top 10
"""

import html
import json
import re
import sys

import requests
import typer


# ---------------------------------------------------------------------------
# 1. Ligação à API
# ---------------------------------------------------------------------------

BASE = "https://wger.de/api/v2/"
CABECALHOS = {"User-Agent": "fitcli/1.0 (TP1 ALPCD - Universidade do Minho)"}
INGLES = 2  # id da língua inglesa na wger

app = typer.Typer(help="Pesquisa exercícios físicos na API wger.")


@app.callback()
def principal():
    """Pesquisa exercícios físicos na API wger."""
    # com o callback, o typer exige sempre o nome do comando (top, search...),
    # mesmo enquanto a CLI só tem um comando


def pedido(url, params=None):
    """Faz um GET à API e devolve o JSON. Se o status não for 200, mostra o erro e sai."""
    if not url.startswith("http"):
        url = BASE + url
    try:
        r = requests.get(url, params=params, headers=CABECALHOS, timeout=20)
    except requests.RequestException as erro:
        typer.echo(f"Erro de ligação à API: {erro}", err=True)
        raise typer.Exit(1)
    if r.status_code == 404:
        typer.echo("Não encontrado (404).", err=True)
        raise typer.Exit(1)
    if r.status_code != 200:
        typer.echo(f"A API respondeu com o código {r.status_code}.", err=True)
        raise typer.Exit(1)
    return r.json()


# ---------------------------------------------------------------------------
# 2. Tratar os dados de um exercício
# ---------------------------------------------------------------------------

def traducao_inglesa(ex):
    """Devolve a tradução em inglês de um exercício (ou None se não houver)."""
    for t in ex["translations"]:
        if t["language"] == INGLES:
            return t
    return None


def limpar_html(texto):
    """Tira as etiquetas HTML da descrição com expressões regulares."""
    if texto is None:
        return ""
    texto = re.sub(r"<[^>]+>", " ", texto)   # <p>, <li>, </ol> ... passam a espaço
    texto = html.unescape(texto)              # &amp; passa a &
    texto = re.sub(r"\s+", " ", texto)        # vários espaços seguidos passam a um só
    return texto.strip()


def musculos(ex):
    """Nomes dos músculos (principais e secundários), com o nome comum se existir."""
    nomes = []
    for m in ex["muscles"] + ex["muscles_secondary"]:
        if m["name_en"]:
            nomes.append(m["name_en"])
        else:
            nomes.append(m["name"])
    return nomes


def resumo(ex):
    """O dicionário que se mostra ao utilizador."""
    equipamento = []
    for e in ex["equipment"]:
        equipamento.append(e["name"])
    return {
        "id": ex["id"],
        "name": traducao_inglesa(ex)["name"],
        "category": ex["category"]["name"],
        "equipment": equipamento,
        "muscles": musculos(ex),
    }


def exercicios(filtros, maximo=None):
    """Lista de exercícios em inglês que cumprem os filtros (no máximo 'maximo').

    Vai buscando páginas pelo campo 'next' enquanto houver mais e ainda
    faltarem exercícios. Sem 'maximo', percorre as páginas todas.
    """
    params = {"language": INGLES, "limit": 100}
    if maximo is not None and maximo < 100:
        params["limit"] = maximo  # para o top 3 não descarregar 100 exercícios
    params.update(filtros)

    resultado = []
    url = "exerciseinfo/"
    while url:
        dados = pedido(url, params)
        for ex in dados["results"]:
            if traducao_inglesa(ex) is None:  # há exercícios só noutras línguas
                continue
            resultado.append(ex)
            if maximo is not None and len(resultado) == maximo:
                return resultado
        url = dados["next"]  # None na última página
        params = None        # o link 'next' já traz os parâmetros todos
    return resultado


# ---------------------------------------------------------------------------
# 6. Comandos da CLI
# ---------------------------------------------------------------------------

def escrever_json(dados):
    typer.echo(json.dumps(dados, ensure_ascii=False, indent=2))


@app.command()
def top(n: int = typer.Argument(10, min=1, help="Quantos exercícios mostrar")):
    """a) Os N exercícios mais recentes da base de dados."""
    resultado = []
    for ex in exercicios({"ordering": "-created"}, n):
        resultado.append(resumo(ex))
    escrever_json(resultado)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # para os acentos aparecerem bem no terminal do Windows
    sys.stderr.reconfigure(encoding="utf-8")
    app()
