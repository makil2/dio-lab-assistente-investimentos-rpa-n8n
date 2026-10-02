"""
RPA - Assistente de Investimentos
Lê a tabela de clientes de uma página HTML e envia os dados ao webhook do n8n.

Uso:
    python rpa/rpa_clientes.py

Variáveis de ambiente (opcionais):
    URL_PAGINA   página HTML com a tabela de clientes
    N8N_WEBHOOK  URL do webhook do n8n (ex.: https://SEU-TUNEL.ngrok-free.dev/webhook-test/Clientes)
"""
import os

import requests
from bs4 import BeautifulSoup

URL_PAGINA = os.getenv(
    "URL_PAGINA",
    "https://digitalinnovationone.github.io/dio-lab-assistente-investimentos-rpa-n8n/",
)
N8N_WEBHOOK = os.getenv(
    "N8N_WEBHOOK",
    "https://SEU-TUNEL.ngrok-free.dev/webhook-test/Clientes",
)


def baixar_pagina(url: str) -> str:
    """1) Baixa o HTML da página."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def extrair_clientes(html: str) -> list[dict]:
    """2) Lê a tabela #clientes e devolve uma lista de dicionários."""
    soup = BeautifulSoup(html, "html.parser")
    linhas = soup.select("#clientes tbody tr")

    clientes = []
    for linha in linhas:
        colunas = linha.find_all("td")
        if len(colunas) < 4:
            continue
        clientes.append(
            {
                "nome": colunas[0].get_text(strip=True),
                "email": colunas[1].get_text(strip=True),
                "saldo": colunas[2].get_text(strip=True),
                "perfil": colunas[3].get_text(strip=True),
            }
        )
    return clientes


def enviar_para_n8n(clientes: list[dict]) -> requests.Response:
    """3) Envia os clientes ao webhook do n8n."""
    return requests.post(
        N8N_WEBHOOK,
        json={"clientes": clientes},
        headers={"Content-Type": "application/json"},
        timeout=60,
    )


def main() -> None:
    html = baixar_pagina(URL_PAGINA)
    clientes = extrair_clientes(html)

    print("Clientes encontrados:", len(clientes))
    print("Exemplo 1º cliente:", clientes[0] if clientes else "nenhum")

    resp = enviar_para_n8n(clientes)
    print("Status:", resp.status_code)
    print("Resposta (primeiros 1500 chars):")
    print(resp.text[:1500])


if __name__ == "__main__":
    main()
