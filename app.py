import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_URL = "https://api.api-futebol.com.br/v1"
TOKEN = os.getenv("API_FUTEBOL_TOKEN", "Bearer live_9729ce5b6070a048dd86bdf1835099")
HEADERS = {"Authorization": TOKEN, "User-Agent": "Mozilla/5.0"}


@app.route("/")
def home():
    return jsonify(
        {
            "status": "API online",
            "mensagem": "Acesse /tabela para ver a classificação atualizada",
        }
    )


@app.route("/tabela")
def obter_tabela():
    try:
        # 1. Consulta a lista de campeonatos liberados
        camps_res = requests.get(
            f"{BASE_URL}/campeonatos", headers=HEADERS, timeout=10
        )

        if camps_res.status_code != 200:
            return (
                jsonify(
                    {
                        "erro": "A API recusou a listagem de campeonatos",
                        "status_code": camps_res.status_code,
                        "resposta_api": camps_res.text,
                    }
                ),
                camps_res.status_code,
            )

        campeonatos = camps_res.json()

        # 2. Procura a Série A independente de maiúsculas/minúsculas
        serie_a = None
        if isinstance(campeonatos, list):
            for c in campeonatos:
                nome = str(c.get("nome", "")).lower()
                nome_pop = str(c.get("nome_popular", "")).lower()
                if "série a" in nome or "brasileirão" in nome_pop or "serie a" in nome:
                    serie_a = c
                    break

        if not serie_a:
            return (
                jsonify(
                    {
                        "erro": "Série A não encontrada na lista liberada.",
                        "campeonatos_disponiveis": campeonatos,
                    }
                ),
                404,
            )

        camp_id = serie_a.get("campeonato_id")

        # 3. Busca a tabela do campeonato encontrado
        tabela_res = requests.get(
            f"{BASE_URL}/campeonatos/{camp_id}/tabela", headers=HEADERS, timeout=10
        )

        if tabela_res.status_code == 200:
            return jsonify(tabela_res.json())
        else:
            return (
                jsonify(
                    {
                        "erro": f"Erro ao buscar tabela do ID {camp_id}",
                        "status_code": tabela_res.status_code,
                        "resposta_api": tabela_res.text,
                    }
                ),
                tabela_res.status_code,
            )

    except Exception as e:
        return jsonify({"erro": "Erro interno no servidor", "detalhes": str(e)}), 500


if __name__ == "__main__":
    app.run()
