from flask import Flask, jsonify, render_template_string
from scraper import buscar_dados_serie_a

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Brasileirão Série A - Tabela Oficial</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f1016; color: #fff; margin: 0; padding: 20px; }
        h1 { color: #00ff88; text-align: center; font-size: 24px; }
        p { text-align: center; color: #888; font-size: 14px; }
        
        .main-container { display: flex; flex-direction: column; align-items: center; gap: 20px; max-width: 800px; margin: 0 auto; }
        
        /* Tabela Estilo Série B */
        .tabela-box { background: #181a26; width: 100%; border-radius: 12px; padding: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.4); }
        .tabela-box h3 { margin-top: 0; color: #fff; border-bottom: 1px solid #2a2d3d; padding-bottom: 10px; font-size: 18px; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th { color: #888; font-size: 12px; text-transform: uppercase; padding: 10px; border-bottom: 1px solid #2a2d3d; }
        td { padding: 12px 10px; border-bottom: 1px solid #1f2232; font-size: 14px; align-items: center; }
        
        .pos-badge { display: inline-block; width: 24px; height: 24px; line-height: 24px; text-align: center; background: #222638; border-radius: 6px; font-weight: bold; font-size: 12px; color: #aaa; }
        .pos-1 { background: #00b894; color: #fff; }
        .pos-g4 { background: #0984e3; color: #fff; }
        .pos-z4 { background: #d63031; color: #fff; }
        
        .team-info { display: flex; align-items: center; gap: 10px; }
        .team-logo { width: 22px; height: 22px; object-fit: contain; }
        
        /* Caixa de Partidas */
        .jogos-container { display: flex; flex-wrap: wrap; gap: 15px; width: 100%; justify-content: center; }
        .box { background: #181a26; border-radius: 10px; padding: 15px; width: 260px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border-left: 4px solid #00ff88; }
        .placar { font-size: 18px; font-weight: bold; color: #ffcc00; margin: 8px 0; }
        .detalhes { font-size: 11px; color: #aaa; margin-top: 4px; }
        
        .firework { position: absolute; width: 6px; height: 6px; border-radius: 50%; animation: explode 1s ease-out forwards; z-index: 999; }
        @keyframes explode {
            0% { transform: scale(1); opacity: 1; }
            100% { transform: scale(40); opacity: 0; }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div>
            <h1>Brasileirão Série A - Jogos e Tabela Oficial</h1>
            <p>Sincronizado automaticamente com escudos, classificação e fogos em tempo real.</p>
        </div>

        <div class="tabela-box">
            <h3>Classificação Geral</h3>
            <table>
                <thead>
                    <tr>
                        <th style="width: 40px;">POS</th>
                        <th>TIME</th>
                        <th style="text-align: right;">PTS</th>
                    </tr>
                </thead>
                <tbody id="tabela-corpo">
                    <tr><td colspan="3" style="text-align: center;">Carregando classificação...</td></tr>
                </tbody>
            </table>
        </div>

        <div style="width: 100%;">
            <h3 style="color: #00ff88; text-align: left; margin-bottom: 10px;">Partidas de Hoje</h3>
            <div class="jogos-container" id="conteudo-jogos">Carregando partidas...</div>
        </div>
    </div>

    <script>
        function dispararFogos() {
            for (let i = 0; i < 8; i++) {
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

                // Monta Tabela Completa
                let tabelaHtml = "";
                let listaTimes = dados.tabela_pontos || [];
                listaTimes.forEach(t => {
                    let badgeClass = "pos-badge";
                    if (t.posicao === 1) badgeClass += " pos-1";
                    else if (t.posicao <= 4) badgeClass += " pos-g4";
                    else if (t.posicao >= 17) badgeClass += " pos-z4";

                    tabelaHtml += `<tr>
                        <td><span class="${badgeClass}">${t.posicao}</span></td>
                        <td>
                            <div class="team-info">
                                ${t.logo ? `<img src="${t.logo}" class="team-logo">` : ''}
                                <strong>${t.time}</strong>
                            </div>
                        </td>
                        <td style="text-align: right; font-weight: bold; color: #ffcc00;">${t.pontos}</td>
                    </tr>`;
                });
                document.getElementById('tabela-corpo').innerHTML = tabelaHtml || "<tr><td colspan='3'>Sem dados</td></tr>";

                // Monta Jogos
                let jogosHtml = "";
                let temGol = false;
                let partidas = dados.partidas || {};

                for (let status in partidas) {
                    if (partidas[status].length > 0) {
                        partidas[status].forEach(p => {
                            if (p.gols && p.gols.length > 0) temGol = true;
                            jogosHtml += `<div class="box">
                                <div style="font-size: 12px; color: #888; text-transform: uppercase; font-weight: bold;">${status}</div>
                                <div style="font-weight: bold; margin-top: 4px;">${p.mandante} vs ${p.visitante}</div>
                                <div class="placar">${p.placar} <span style="font-size: 12px; color: #aaa;">(${p.horario})</span></div>
                                <div class="detalhes">⚽ Gols: ${p.gols.join(', ') || 'Nenhum'}</div>
                                <div class="detalhes">🟨 Amarelos: ${p.cartoes_amarelos.join(', ') || 'Nenhum'}</div>
                            </div>`;
                        });
                    }
                }
                document.getElementById('conteudo-jogos').innerHTML = jogosHtml || "<p style='color: #888;'>Nenhuma partida encontrada para hoje.</p>";

                if (temGol) dispararFogos();

            } catch (e) {
                console.error("Erro ao carregar dados", e);
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


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
