import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.api.adzuna import buscar_vagas_na_api, AdzunaError
from src.utils.dados import salvar_vagas, carregar_vagas


def main():
    parser = argparse.ArgumentParser(
        description="Coleta vagas de emprego reais da Adzuna API e "
        "salva em data/vagas.json"
    )
    parser.add_argument(
        "--termo",
        default="developer",
        help="Palavra-chave de busca na Adzuna (padrão: 'developer')",
    )
    parser.add_argument(
        "--paginas",
        type=int,
        default=2,
        help="Quantidade de páginas a coletar (padrão: 2, ~100 vagas)",
    )
    parser.add_argument(
        "--localizacao",
        default=None,
        help="Filtro opcional de localização (ex: 'Brasília')",
    )
    parser.add_argument(
        "--anexar",
        action="store_true",
        help="Anexa os resultados aos já existentes em vez de substituir",
    )

    argumentos = parser.parse_args()

    print(f"Coletando vagas da Adzuna para o termo: '{argumentos.termo}'...")

    try:
        novas_vagas = buscar_vagas_na_api(
            termo=argumentos.termo,
            quantidade_paginas=argumentos.paginas,
            localizacao=argumentos.localizacao,
        )
    except AdzunaError as erro:
        print(f"\nErro: {erro}")
        print(
            "\nDica: copie '.env.example' para '.env' e preencha "
            "ADZUNA_APP_ID e ADZUNA_APP_KEY com suas credenciais "
            "(https://developer.adzuna.com/)."
        )
        sys.exit(1)

    if not novas_vagas:
        print("Nenhuma vaga encontrada para os parâmetros informados.")
        sys.exit(0)

    if argumentos.anexar:
        vagas_existentes = carregar_vagas()
        ids_existentes = {vaga.get("id") for vaga in vagas_existentes}
        novas_vagas = [v for v in novas_vagas if v.get("id") not in ids_existentes]
        vagas_finais = vagas_existentes + novas_vagas
    else:
        # Reatribui IDs sequenciais simples para facilitar a leitura.
        vagas_finais = novas_vagas
        for indice, vaga in enumerate(vagas_finais, start=1):
            vaga["id"] = indice

    salvar_vagas(vagas_finais)

    print(f"{len(novas_vagas)} vaga(s) coletada(s).")
    print(f"Base local agora possui {len(vagas_finais)} vaga(s).")
    print("Arquivo salvo em: data/vagas.json")


if __name__ == "__main__":
    main()
