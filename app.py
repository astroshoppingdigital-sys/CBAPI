from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Libera o acesso para o seu site no Google Studio ler a API sem erros de CORS

@app.route('/')
def home():
    return jsonify({
        "status": "API online",
        "mensagem": "Acesse /tabela para ver a classificação do Brasileirão"
    })

@app.route('/tabela', methods=['GET'])
def get_tabela():
    url = "https://api.api-futebol.com.br/v1/campeonatos/10/tabela"
    headers = {
        "Authorization": "Bearer live_819da218da3a144b67fa9723cb9f67"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"erro": "Falha ao obter dados da API oficial"}), response.status_code
            
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)