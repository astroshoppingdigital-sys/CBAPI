import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Endpoint oficial da Tabela do Brasileirão Série A (ID 10)
API_URL = "https://api.api-futebol.com.br/v1/campeonatos/10/tabela"
API_KEY = "test_c38e25632ec1bfd185c43f2d4ac4ef"

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "API online",
        "mensagem": "Acesse /tabela para ver a classificação do Brasileirão"
    })

@app.route("/tabela", methods=["GET"])
def obter_tabela():
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "erro": "Erro ao consultar API do Brasileirão",
                "status_code": response.status_code,
                "detalhes": response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({"erro": f"Falha na requisição: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)