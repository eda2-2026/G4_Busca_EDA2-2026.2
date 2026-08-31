import json
import os
from typing import List, Dict, Any

# Caminho padrão do arquivo de dados, relativo à raiz do projeto.
CAMINHO_PADRAO = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "vagas.json"
)


def carregar_vagas(caminho: str = CAMINHO_PADRAO) -> List[Dict[str, Any]]:

    caminho_absoluto = os.path.abspath(caminho)

    if not os.path.exists(caminho_absoluto):
        return []

    with open(caminho_absoluto, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_vagas(vagas: List[Dict[str, Any]], caminho: str = CAMINHO_PADRAO) -> None:
    """Salva a lista de vagas em um arquivo JSON, formatado e legível."""
    caminho_absoluto = os.path.abspath(caminho)
    os.makedirs(os.path.dirname(caminho_absoluto), exist_ok=True)

    with open(caminho_absoluto, "w", encoding="utf-8") as arquivo:
        json.dump(vagas, arquivo, ensure_ascii=False, indent=2)


def ordenar_por_campo(
    vagas: List[Dict[str, Any]], campo: str = "titulo"
) -> List[Dict[str, Any]]:
    
    return sorted(vagas, key=lambda vaga: str(vaga.get(campo, "")).strip().lower())
