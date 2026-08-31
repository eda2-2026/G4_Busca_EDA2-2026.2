import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from busca.busca_binaria import busca_binaria, busca_binaria_exata
from busca.busca_sequencial import busca_sequencial, busca_sequencial_exata
from utils.dados import ordenar_por_campo


def _vaga(id_, titulo):
    return {
        "id": id_,
        "titulo": titulo,
        "empresa": "Empresa Teste",
        "localizacao": "Brasília",
        "descricao": "Descrição de teste.",
        "url": "https://exemplo.invalido",
    }


VAGAS_EXEMPLO_DESORDENADAS = [
    _vaga(1, "Engenheiro de Software"),
    _vaga(2, "Analista de Dados"),
    _vaga(3, "Desenvolvedor Frontend"),
    _vaga(4, "Analista de Sistemas"),
    _vaga(5, "Desenvolvedor Backend"),
]

VAGAS_ORDENADAS = ordenar_por_campo(VAGAS_EXEMPLO_DESORDENADAS)


def test_elemento_existe():
    resultados, comparacoes = busca_binaria(VAGAS_ORDENADAS, "Desenvolvedor Backend")
    assert len(resultados) == 1
    assert resultados[0]["titulo"] == "Desenvolvedor Backend"
    assert comparacoes > 0


def test_elemento_nao_existe():
    resultados, _ = busca_binaria(VAGAS_ORDENADAS, "Cientista de Dados")
    assert resultados == []


def test_lista_com_apenas_um_elemento():
    unica = ordenar_por_campo([_vaga(1, "Desenvolvedor Backend")])

    resultados, comparacoes = busca_binaria(unica, "Desenvolvedor Backend")
    assert len(resultados) == 1
    assert comparacoes >= 1

    resultados, _ = busca_binaria(unica, "Analista")
    assert resultados == []


def test_lista_vazia():
    resultados, comparacoes = busca_binaria([], "Desenvolvedor")
    assert resultados == []
    assert comparacoes == 0


def test_elementos_repetidos():
    vagas_repetidas = ordenar_por_campo(
        VAGAS_EXEMPLO_DESORDENADAS + [_vaga(6, "Desenvolvedor Backend")]
    )
    resultados, _ = busca_binaria(vagas_repetidas, "Desenvolvedor Backend")
    assert len(resultados) == 2


def test_busca_exata_complexidade_logaritmica():
    vagas_grandes = ordenar_por_campo(
        [_vaga(i, f"Cargo Numero {i:06d}") for i in range(1, 100_001)]
    )

    _, comparacoes = busca_binaria_exata(vagas_grandes, "Cargo Numero 099999")

    limite_teorico = math.ceil(math.log2(len(vagas_grandes))) + 1
    assert comparacoes <= limite_teorico


def test_sequencial_e_binaria_produzem_resultados_equivalentes():
    termos_para_testar = [
        "Desenvolvedor",
        "Analista",
        "Engenheiro de Software",
        "Vaga Inexistente",
    ]

    for termo in termos_para_testar:
        resultados_sequencial, _ = busca_sequencial(VAGAS_EXEMPLO_DESORDENADAS, termo)
        resultados_binaria, _ = busca_binaria(VAGAS_ORDENADAS, termo)

        titulos_sequencial = {vaga["titulo"] for vaga in resultados_sequencial}
        titulos_binaria = {vaga["titulo"] for vaga in resultados_binaria}

        assert titulos_sequencial == titulos_binaria


def test_exata_sequencial_e_binaria_concordam_sobre_existencia():
    termos_para_testar = [
        "Desenvolvedor Backend",
        "Analista de Sistemas",
        "Vaga Inexistente",
    ]

    for termo in termos_para_testar:
        vaga_sequencial, _ = busca_sequencial_exata(VAGAS_EXEMPLO_DESORDENADAS, termo)
        vaga_binaria, _ = busca_binaria_exata(VAGAS_ORDENADAS, termo)

        encontrou_sequencial = vaga_sequencial is not None
        encontrou_binaria = vaga_binaria is not None

        assert encontrou_sequencial == encontrou_binaria
