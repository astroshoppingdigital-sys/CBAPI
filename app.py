import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

def buscar_dados_serie_a():
    # URL da Série A (ou altere para bra.1 / bra.2 conforme sua preferência)
    url_tabela = "https://site.web.api.espn.com/apis/v2/sports/soccer/bra.1/standings"
    url_scoreboard = "https://site.web.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard"
    
    dados_retorno = {
        "tabela_pontos": [],
        "partidas": {
            "AO VIVO": [],
            "PRÓXIMOS": [],
            "ENCERRADOS": []
        }
    }

    # 1. Buscando a Tabela de Pontos
    try:
        resp_tab = requests.get(url_tabela, headers=HEADERS, timeout=15)
        if resp_tab.status_code == 403:
            resp_tab = requests.get("https://cdn.espn.com/core/soccer/standings?league=bra.1&xhr=1", headers=HEADERS, timeout=15)
        
        resp_tab.raise_for_status()
        tabela_json = resp_tab.json()

        entries = []
        try:
            entries = tabela_json.get("children", [{}])[0].get("standings", {}).get("entries", [])
        except Exception:
            pass

        if not entries and "content" in tabela_json:
            try:
                entries = tabela_json.get("content", {}).get("standings", {}).get("groups", [{}])[0].get("standings", {}).get("entries", [])
            except Exception:
                pass

        for idx, entry in enumerate(entries, 1):
            team = entry.get("team", {})
            stats = {stat.get("name"): stat.get("value") for stat in entry.get("stats", [])}

            dados_retorno["tabela_pontos"].append({
                "posicao": idx,
                "time": team.get("displayName"),
                "sigla": team.get("abbreviation"),
                "logo": team.get("logos", [{}])[0].get("href") if team.get("logos") else None,
                "pontos": int(stats.get("points", 0)),
                "jogos": int(stats.get("gamesPlayed", 0)),
                "vitorias": int(stats.get("wins", 0)),
                "empates": int(stats.get("ties", 0)),
                "derrotas": int(stats.get("losses", 0)),
                "saldo": int(stats.get("pointDifferential", 0))
            })
    except Exception as e:
        print(f"Erro ao buscar tabela: {e}")

    # 2. Buscando os Jogos / Placares com Blindagem de Estado
    try:
        resp_jogos = requests.get(url_scoreboard, headers=HEADERS, timeout=15)
        resp_jogos.raise_for_status()
        jogos_json = resp_jogos.json()

        events = jogos_json.get("events", [])
        for event in events:
            competition = event.get("competitions", [{}])[0]
            competitors = competition.get("competitors", [])

            mandante_obj = next((c for c in competitors if c.get("homeAway") == "home"), {})
            visitante_obj = next((c for c in competitors if c.get("homeAway") == "away"), {})

            # Tratativa de status segura baseada na API da ESPN
            status_obj = event.get("status", {})
            status_type = status_obj.get("type", {})
            
            state = status_type.get("state") # "pre", "in", "post"
            completed = status_type.get("completed", False)
            clock = status_obj.get("displayClock", "")
            description = status_type.get("description", "")

            # Definindo a categoria de forma blindada para evitar encerramento falso
            if state == "pre":
                categoria = "PRÓXIMOS"
                status_texto = description or "Agendado"
            elif state == "in":
                categoria = "AO VIVO"
                # Se estiver no intervalo ou acréscimo, mantém o relógio/descrição fiel
                status_texto = f"{description} ({clock}'+)" if clock and clock != "0" else description
                if not status_texto:
                    status_texto = "AO VIVO"
            elif state == "post" or completed:
                categoria = "ENCERRADOS"
                status_texto = "Encerrado"
            else:
                categoria = "PRÓXIMOS"
                status_texto = description or "Aguardando"

            partida_info = {
                "mandante": mandante_obj.get("team", {}).get("displayName", "Mandante"),
                "visitante": visitante_obj.get("team", {}).get("displayName", "Visitante"),
                "placar": f"{mandante_obj.get('score', '0')} x {visitante_obj.get('score', '0')}",
                "horario": event.get("date", "")[11:16], # Pega HH:MM da data ISO
                "status_detalhado": status_texto,
                "gols": [],         # Caso sua API extraia lances futuramente
                "cartoes_amarelos": []
            }

            dados_retorno["partidas"][categoria].append(partida_info)

    except Exception as e:
        print(f"Erro ao buscar jogos: {e}")

    return dados_retorno
