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