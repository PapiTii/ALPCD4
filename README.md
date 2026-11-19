# fitcli — TP1 de ALPCD 2026/27 · Grupo 4

## Elementos do grupo

| Nome | N.º de aluno |
|---|---|
| Tiago Correia | A114093 |
| Tomás Fernandes | A111541 |
| Cristiano Azevedo | A114444 |

CLI em Python para explorar a API pública [wger](https://wger.de/api/v2/) (exercícios, músculos, equipamento).
Usa `requests` (pedidos à API), `re` (limpeza e análise de texto) e `typer` (a linha de comandos).

## Instalar

```
pip install -r requirements.txt
```

## Comandos

| Alínea | Comando | O que faz |
|---|---|---|
| a) | `python fitcli.py top 10` | Os 10 exercícios mais recentes (nome, categoria, equipamento, músculos), em JSON |
| b) | `python fitcli.py search biceps 5` | Exercícios de um músculo **ou** de uma categoria |
| b) | `python fitcli.py search biceps 5 -c arms` | Músculo **e** categoria ao mesmo tempo |
| extra | `python fitcli.py grupos` | Lista os músculos e as categorias aceites |

`python fitcli.py --help` e `python fitcli.py <comando> --help` mostram a ajuda.

## Boas práticas da API

- Cabeçalho `User-Agent` identificativo em todos os pedidos.
- O código de estado é verificado: um 404 e os outros erros dão uma mensagem clara, sem rebentar o programa.
- Paginação: segue-se o campo `next` até ao fim, mas só enquanto são precisos mais resultados.
- `language=2` (inglês), e ignoram-se os exercícios que não têm tradução inglesa.
