import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)

# =========================================================
# CONFIGURAÇÕES DA API DO BRASILEIRÃO
# =========================================================
# URL exata para puxar as partidas / placar ao vivo
API_URL = "https://api.api-futebol.com.br/v1/partidas"

# Sua chave de teste do Brasileirão API
API_KEY = "test_c38e25632ec1bfd185c43f2d4ac4ef"
# =========================================================


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "status": "API online",
            "mensagem": "Acesse /placar para ver o placar do Brasileirão",
        }
    )


@app.route("/placar", methods=["GET"])
def obter_placar():
    # A API do Brasileirão exige a chave no formato Bearer Token
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(API_URL, headers=headers, timeout=10)

        if response.status_code == 200:
            return jsonify(
                {"status": "sucesso", "dados": response.json()}
            ), 200
        else:
            return jsonify(
                {
                    "status": "erro",
                    "mensagem": f"Erro na API do Brasileirão: {response.status_code}",
                    "detalhes": response.text,
                }
            ), response.status_code

    except Exception as e:
        return jsonify(
            {"status": "erro", "mensagem": f"Falha na conexão: {str(e)}"}
        ), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)