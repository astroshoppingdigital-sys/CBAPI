import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# URL oficial da API Futebol para o Brasileirão Série A (ID 10)
API_URL = "https://api.api-futebol.com.br/v1/campeonatos/10/tabela"

# Sua chave de teste configurada diretamente
TOKEN = "Bearer test_c38e25632ec1bfd185c43f2d4ac4ef"

HEADERS = {"Authorization": TOKEN, "User-Agent": "Mozilla/5.0"}


@app.route("/")
def home():
    return jsonify(
        {
            "status": "API online",
            "mensagem": "Acesse /tabela para ver a classificação do Brasileirão",
        }
    )


@app.route("/tabela")
def obter_tabela():
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=10)

        # Se a API externa responder com sucesso
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return (
                jsonify(
                    {
                        "erro": "A API de futebol recusou a conexão",
                        "status_code": response.status_code,
                        "resposta": response.text,
                    }
                ),
                response.status_code,
            )

    except Exception as e:
        return (
            jsonify({"erro": "Falha ao obter dados da API oficial", "detalhes": str(e)}),
            500,
        )


if __name__ == "__main__":
    app.run()
