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
        # 1. Consulta a lista de campeonatos liberados na sua chave live
        camps_res = requests.get(
            f"{BASE_URL}/campeonatos", headers=HEADERS, timeout=10
        )

        if camps_res.status_code != 200:
            return (
                jsonify(
                    {
                        "erro": "Falha ao consultar campeonatos",
                        "resposta": camps_res.text,
                    }
                ),
                camps_res.status_code,
            )

        campeonatos = camps_res.json()

        # 2. Encontra automaticamente o ID do Brasileirão Série A ativo
        serie_a = next(
            (
                c
                for c in campeonatos
                if "Série A" in c.get("nome", "")
                or "Brasileirão" in c.get("nome_popular", "")
            ),
            None,
        )

        if not serie_a:
            return (
                jsonify(
                    {
                        "erro": "Brasileirão Série A não encontrado nos campeonatos liberados."
                    }
                ),
                404,
            )

        camp_id = serie_a["campeonato_id"]

        # 3. Busca a tabela atualizada da edição vigente
        tabela_res = requests.get(
            f"{BASE_URL}/campeonatos/{camp_id}/tabela", headers=HEADERS, timeout=10
        )

        if tabela_res.status_code == 200:
            return jsonify(tabela_res.json())
        else:
            return (
                jsonify(
                    {
                        "erro": f"Erro ao buscar tabela do campeonato ID {camp_id}",
                        "resposta": tabela_res.text,
                    }
                ),
                tabela_res.status_code,
            )

    except Exception as e:
        return jsonify({"erro": "Falha na requisição", "detalhes": str(e)}), 500


if __name__ == "__main__":
    app.run()
