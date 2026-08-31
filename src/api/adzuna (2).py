
import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/{pais}/search/{pagina}"


class AdzunaError(Exception):
    """Erro genérico ao comunicar com a Adzuna API."""


def _verificar_credenciais() -> None:
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise AdzunaError(
            "Credenciais da Adzuna não encontradas. Defina ADZUNA_APP_ID "
            "e ADZUNA_APP_KEY no arquivo .env (veja .env.example)."
        )


def buscar_vagas_na_api(
    termo: str = "developer",
    pais: str = "br",
    quantidade_paginas: int = 1,
    resultados_por_pagina: int = 50,
    localizacao: Optional[str] = None,
) -> List[Dict[str, Any]]:

    _verificar_credenciais()

    todas_vagas: List[Dict[str, Any]] = []

    for pagina in range(1, quantidade_paginas + 1):
        url = BASE_URL.format(pais=pais, pagina=pagina)

        parametros = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "what": termo,
            "results_per_page": resultados_por_pagina,
            "content-type": "application/json",
        }

        if localizacao:
            parametros["where"] = localizacao

        resposta = requests.get(url, params=parametros, timeout=15)

        if resposta.status_code != 200:
            raise AdzunaError(
                f"Erro ao consultar a Adzuna API (status {resposta.status_code}): "
                f"{resposta.text[:300]}"
            )

        dados = resposta.json()
        resultados = dados.get("results", [])

        if not resultados:
            break

        for vaga_bruta in resultados:
            todas_vagas.append(_converter_vaga(vaga_bruta))

    return todas_vagas


def _converter_vaga(vaga_bruta: Dict[str, Any]) -> Dict[str, Any]:

    empresa = vaga_bruta.get("company", {}) or {}
    localizacao = vaga_bruta.get("location", {}) or {}

    return {
        "id": vaga_bruta.get("id"),
        "titulo": vaga_bruta.get("title", "").strip(),
        "empresa": empresa.get("display_name", "Não informado"),
        "localizacao": localizacao.get("display_name", "Não informado"),
        "descricao": vaga_bruta.get("description", "").strip(),
        "url": vaga_bruta.get("redirect_url", ""),
    }
