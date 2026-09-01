import os
import sys
import time
import glob

from flask import Flask, jsonify, request, send_from_directory

sys.path.insert(0, os.path.dirname(__file__))

from busca.busca_sequencial import busca_sequencial, busca_sequencial_exata
from busca.busca_binaria import busca_binaria, busca_binaria_exata
from utils.dados import carregar_vagas, ordenar_por_campo


RAIZ_PROJETO = os.path.join(os.path.dirname(__file__), "..")
PASTA_FRONTEND = os.path.join(RAIZ_PROJETO, "frontend")
PASTA_DADOS = os.path.join(RAIZ_PROJETO, "data")

app = Flask(__name__, static_folder=None)

_cache_vagas = None
_cache_vagas_ordenadas = None


def obter_vagas():
    global _cache_vagas, _cache_vagas_ordenadas

    if _cache_vagas is None:
        _cache_vagas = carregar_vagas()
        _cache_vagas_ordenadas = ordenar_por_campo(_cache_vagas, campo="titulo")

    return _cache_vagas, _cache_vagas_ordenadas


def recarregar_cache():
    global _cache_vagas, _cache_vagas_ordenadas
    _cache_vagas = None
    _cache_vagas_ordenadas = None


@app.route("/")
def pagina_principal():
    return send_from_directory(PASTA_FRONTEND, "index.html")


@app.route("/css/<path:nome_arquivo>")
def arquivos_css(nome_arquivo):
    return send_from_directory(os.path.join(PASTA_FRONTEND, "css"), nome_arquivo)


@app.route("/js/<path:nome_arquivo>")
def arquivos_js(nome_arquivo):
    return send_from_directory(os.path.join(PASTA_FRONTEND, "js"), nome_arquivo)


@app.route("/api/vagas")
def listar_vagas():
    vagas, _ = obter_vagas()
    return jsonify({"total": len(vagas), "vagas": vagas})


@app.route("/api/buscar")
def rota_buscar():
    termo = request.args.get("termo", "").strip()
    algoritmo = request.args.get("algoritmo", "sequencial").strip().lower()
    campo = request.args.get("campo", "titulo").strip()

    if not termo:
        return jsonify({"erro": "Parâmetro 'termo' é obrigatório."}), 400

    vagas, vagas_ordenadas = obter_vagas()

    inicio = time.perf_counter()

    if algoritmo == "binaria":
        resultados, comparacoes = busca_binaria(vagas_ordenadas, termo, campo)
    elif algoritmo == "sequencial":
        resultados, comparacoes = busca_sequencial(vagas, termo, campo)
    else:
        return (
            jsonify({"erro": "Parâmetro 'algoritmo' deve ser 'sequencial' ou 'binaria'."}),
            400,
        )

    tempo_execucao = time.perf_counter() - inicio

    return jsonify(
        {
            "termo": termo,
            "algoritmo": algoritmo,
            "campo": campo,
            "total_encontrado": len(resultados),
            "comparacoes": comparacoes,
            "tempo_execucao_segundos": tempo_execucao,
            "vagas": resultados,
        }
    )


@app.route("/api/comparar")
def rota_comparar():
    termo = request.args.get("termo", "").strip()
    campo = request.args.get("campo", "titulo").strip()

    if not termo:
        return jsonify({"erro": "Parâmetro 'termo' é obrigatório."}), 400

    vagas, vagas_ordenadas = obter_vagas()

    inicio_sequencial = time.perf_counter()
    vaga_sequencial, comparacoes_sequencial = busca_sequencial_exata(vagas, termo, campo)
    tempo_sequencial = time.perf_counter() - inicio_sequencial

    inicio_binaria = time.perf_counter()
    vaga_binaria, comparacoes_binaria = busca_binaria_exata(vagas_ordenadas, termo, campo)
    tempo_binaria = time.perf_counter() - inicio_binaria

    resultados_prefixo, _ = busca_binaria(vagas_ordenadas, termo, campo)

    return jsonify(
        {
            "termo": termo,
            "campo": campo,
            "total_vagas_na_base": len(vagas),
            "total_encontrado_prefixo": len(resultados_prefixo),
            "sequencial": {
                "encontrado": vaga_sequencial is not None,
                "comparacoes": comparacoes_sequencial,
                "tempo_execucao_segundos": tempo_sequencial,
                "vaga": vaga_sequencial,
            },
            "binaria": {
                "encontrado": vaga_binaria is not None,
                "comparacoes": comparacoes_binaria,
                "tempo_execucao_segundos": tempo_binaria,
                "vaga": vaga_binaria,
            },
        }
    )


@app.route("/api/experimentos")
def rota_experimentos():
    padrao_arquivos = os.path.join(PASTA_DADOS, "vagas_teste_*.json")
    arquivos = sorted(
        glob.glob(padrao_arquivos),
        key=lambda caminho: int(
            os.path.basename(caminho).replace("vagas_teste_", "").replace(".json", "")
        ),
    )

    if not arquivos:
        return (
            jsonify(
                {
                    "erro": (
                        "Nenhuma massa de dados de teste encontrada. "
                        "Execute: python scripts/gerar_dados_teste.py"
                    )
                }
            ),
            404,
        )

    termo = request.args.get("termo", "").strip()

    resultados_experimento = []

    for caminho_arquivo in arquivos:
        tamanho = int(
            os.path.basename(caminho_arquivo)
            .replace("vagas_teste_", "")
            .replace(".json", "")
        )

        import json

        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            vagas_teste = json.load(arquivo)

        vagas_teste_ordenadas = ordenar_por_campo(vagas_teste, campo="titulo")


        termo_usado = termo or vagas_teste[len(vagas_teste) // 2]["titulo"]

        inicio_sequencial = time.perf_counter()
        _, comparacoes_sequencial = busca_sequencial_exata(vagas_teste, termo_usado, "titulo")
        tempo_sequencial = time.perf_counter() - inicio_sequencial

        inicio_binaria = time.perf_counter()
        _, comparacoes_binaria = busca_binaria_exata(
            vagas_teste_ordenadas, termo_usado, "titulo"
        )
        tempo_binaria = time.perf_counter() - inicio_binaria

        resultados_experimento.append(
            {
                "tamanho": tamanho,
                "termo_usado": termo_usado,
                "sequencial": {
                    "comparacoes": comparacoes_sequencial,
                    "tempo_execucao_segundos": tempo_sequencial,
                },
                "binaria": {
                    "comparacoes": comparacoes_binaria,
                    "tempo_execucao_segundos": tempo_binaria,
                },
            }
        )

    return jsonify({"resultados": resultados_experimento})


@app.route("/api/recarregar", methods=["POST"])
def rota_recarregar():
    recarregar_cache()
    vagas, _ = obter_vagas()
    return jsonify({"mensagem": "Base recarregada.", "total": len(vagas)})


if __name__ == "__main__":
    porta = int(os.getenv("PORT", 5000))
    print(f"Servindo em: http://127.0.0.1:{porta}")
    app.run(debug=True, port=porta)