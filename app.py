from flask import Flask, jsonify, render_template_string
from scraper import buscar_dados_serie_a

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Brasileirão Série A - Placar e Tabela</title>
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: #fff; margin: 0; padding: 20px; text-align: center; }
        h1 { color: #00ff88; }
        .container { display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 20px; }
        .box { background: #1e1e1e; border-radius: 8px; padding: 15px; width: 280px; margin: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); text-align: left; }
        .placar { font-size: 18px; font-weight: bold; color: #ffcc00; margin: 8px 0; }
        .detalhes { font-size: 12px; color: #ccc; margin-top: 4px; }
        .tabela-box { background: #1a1a2e; margin: 20px auto; padding: 15px; border-radius: 8px; width: 80%; max-width: 500px; text-align: left; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; border-bottom: 1px solid #333; font-size: 14px; }
        th { color: #00ff88; }
        .firework { position: absolute; width: 6px; height: 6px; border-radius: 50%; animation: explode 1s ease-out forwards; }
        @keyframes explode {
            0% { transform: scale(1); opacity: 1; }
            100% { transform: scale(35); opacity: 0; }
        }
    </style>
</head>
<body>
    <h1>Brasileirão Série A - Jogos e Tabela Atualizada</h1>
    <p>Atualização automática com lances, gols e pontuação pós-jogo.</p>

    <div class="tabela-box">
        <h3>Classificação Parcial (Pontos)</h3>
        <table>
            <thead><tr><th>Equipe</th><th style="text-align: right;">Pontos</th></tr></thead>
            <tbody id="tabela-corpo"><tr><td colspan="2">Carregando tabela...</td></tr></tbody>
        </table>
    </div>
    
    <div class="container" id="conteudo">Carregando partidas...</div>

    <script>
        function dispararFogos() {
            for (let i = 0; i < 6; i++) {
                let fw = document.createElement('div');
                fw.className = 'firework';
                fw.style.left = Math.random() * window.innerWidth + 'px';
                fw.style.top = Math.random() * window.innerHeight + 'px';
                fw.style.backgroundColor = ['#ff0055', '#00ff88', '#00ccff', '#ffff00', '#ff6600'][Math.floor(Math.random()*5)];
                document.body.appendChild(fw);
                setTimeout(() => fw.remove(), 1000);
            }
        }

        async function carregarDados() {
            try {
                let resposta = await fetch('/dados');
                let dados = resposta.ok ? await resposta.json() : null;
                
                if (!dados) return;

                // Renderiza Tabela de Pontos
                let tabelaHtml = "";
                let pts = dados.tabela_pontos || {};
                for (let time in pts) {
                    tabelaHtml += `<tr><td>${time}</td><td style="text-align: right; font-weight: bold; color: #ffcc00;">${pts[time]} pts</td></tr>`;
                }
                document.getElementById('tabela-corpo').innerHTML = tabelaHtml || "<tr><td colspan='2'>Sem dados de tabela</td></tr>";

                // Renderiza Partidas por Status
                let html = "";
                let temGol = false;
                let partidas = dados.partidas || {};

                for (let status in partidas) {
                    if (partidas[status].length > 0) {
                        html += `<div style="width: 100%;"><h2>${status.toUpperCase()}</h2></div>`;
                        partidas[status].forEach(p => {
                            if (p.gols && p.gols.length > 0) temGol = true;
                            html += `<div class="box">
                                <strong>${p.mandante} vs ${p.visitante}</strong>
                                <div class="placar">${p.placar} (${p.horario})</div>
                                <div class="detalhes">⚽ Gols: ${p.gols.join(', ') || 'Nenhum'}</div>
                                <div class="detalhes">🟨 Amarelos: ${p.cartoes_amarelos.join(', ') || 'Nenhum'}</div>
                                <div class="detalhes">🟥 Vermelhos: ${p.cartoes_vermelhos.join(', ') || 'Nenhum'}</div>
                            </div>`;
                        });
                    }
                }

                document.getElementById('conteudo').innerHTML = html || "<p>Nenhuma partida encontrada.</p>";
                
                if (temGol) {
                    dispararFogos();
                }
            } catch (e) {
                console.error("Erro ao atualizar dados", e);
            }
        }

        carregarDados();
        setInterval(carregarDados, 30000);
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():
  return render_template_string(HTML_TEMPLATE)


@app.route("/dados", methods=["GET"])
def api_dados():
  return jsonify(buscar_dados_serie_a())


@app.route("/partidas", methods=["GET"])
def listar_todas():
  dados = buscar_dados_serie_a()
  return jsonify(dados["partidas"])


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)