import argparse
import itertools
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.dados import carregar_vagas

CARGOS_BASE = [
    "Desenvolvedor Backend",
    "Desenvolvedor Frontend",
    "Desenvolvedor Full Stack",
    "Desenvolvedor Python",
    "Desenvolvedor Java",
    "Desenvolvedor Mobile",
    "Engenheiro de Software",
    "Engenheiro de Dados",
    "Analista de Dados",
    "Analista de Sistemas",
    "Analista de Suporte",
    "Cientista de Dados",
    "Arquiteto de Software",
    "Administrador de Banco de Dados",
    "Especialista em DevOps",
    "Especialista em QA",
    "Gerente de Projetos de TI",
    "Product Manager",
    "UX Designer",
    "UI Designer",
]

EMPRESAS_BASE = [
    "TechNova", "DataCore", "InovaSoft", "BrasilCode", "CloudWorks",
    "NexaSystems", "Vértice TI", "Prisma Digital", "Alpha Software",
    "Orbita Tech",
]

CIDADES_BASE = [
    "Brasília", "São Paulo", "Rio de Janeiro", "Belo Horizonte",
    "Curitiba", "Porto Alegre", "Salvador", "Recife", "Remoto",
]


def _vagas_sementes():
    reais = carregar_vagas()
    if reais:
        return reais
    return []


def gerar_massa_dados(tamanho: int, sementes) -> list:
    vagas = []

    # Reaproveita vagas reais como parte da massa de dados.
    for vaga in sementes[:tamanho]:
        vagas.append(dict(vaga))

    contador = itertools.count(1)
    while len(vagas) < tamanho:
        indice = next(contador)
        cargo = CARGOS_BASE[indice % len(CARGOS_BASE)]
        empresa = EMPRESAS_BASE[indice % len(EMPRESAS_BASE)]
        cidade = CIDADES_BASE[indice % len(CIDADES_BASE)]

        vagas.append({
            "id": len(vagas) + 1,
            "titulo": f"{cargo} {indice}",
            "empresa": empresa,
            "localizacao": cidade,
            "descricao": f"Vaga sintética gerada para testes de desempenho ({cargo}).",
            "url": "https://exemplo.invalido/vaga/" + str(indice),
        })

    random.shuffle(vagas)
    for indice, vaga in enumerate(vagas, start=1):
        vaga["id"] = indice

    return vagas


def main():
    parser = argparse.ArgumentParser(
        description="Gera massas de dados sintéticas para os experimentos "
        "de desempenho dos algoritmos de busca."
    )
    parser.add_argument(
        "--tamanhos",
        type=int,
        nargs="+",
        default=[100, 1000, 10000, 100000],
        help="Tamanhos das massas de dados a gerar (padrão: 100 1000 10000 100000)",
    )
    parser.add_argument(
        "--saida",
        default=os.path.join(os.path.dirname(__file__), "..", "data"),
        help="Pasta de saída dos arquivos gerados",
    )

    argumentos = parser.parse_args()
    sementes = _vagas_sementes()

    if sementes:
        print(f"Usando {len(sementes)} vaga(s) real(is) da Adzuna como sementes.")
    else:
        print(
            "Nenhuma vaga real encontrada em data/vagas.json. "
            "Gerando massas 100% sintéticas."
        )

    os.makedirs(argumentos.saida, exist_ok=True)

    for tamanho in argumentos.tamanhos:
        massa = gerar_massa_dados(tamanho, sementes)
        caminho = os.path.join(argumentos.saida, f"vagas_teste_{tamanho}.json")

        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(massa, arquivo, ensure_ascii=False, indent=2)

        print(f"Gerado: {caminho} ({len(massa)} vagas)")


if __name__ == "__main__":
    main()
