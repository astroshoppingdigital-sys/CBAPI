from datetime import datetime, timedelta
import requests


def buscar_dados_serie_a():
    url_scoreboard = (
        "https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard"
    )
    url_standings = (
        "https://site.api.espn.com/apis/v2/sports/soccer/bra.1/standings"
    )

    partidas = {"ao_vivo": [], "agendado": [], "encerrado": []}
    tabela_completa = []

    # 1. Puxa a Tabela Oficial de Classificação (Standings) com todos os 20 times
    try:
        resp_standings = requests.get(url_standings, timeout=10)
        if resp_standings.status_code == 200:
            dados_st = resp_standings.json()
            standings = (
                dados_st.get("children", [{}])[0]
                .get("standings", {})
                .get("entries", [])
            )

            for pos, entry in enumerate(standings, start=1):
                team_info = entry.get("team", {})
                nome_time = team_info.get("displayName", "Time")

                logos = team_info.get("logos", [])
                logo_url = logos[0].get("href", "") if logos else ""

                stats = {s.get("name"): s.get("displayValue") for s in entry.get("stats", [])}

                pontos = stats.get("points", "0")
                jogos = stats.get("gamesPlayed", "0")
                vitorias = stats.get("wins", "0")
                derrotas = stats.get("losses", "0")
                empates = stats.get("ties", "0")
                saldo = stats.get("pointDifferential", "0")

                tabela_completa.append({
                    "posicao": pos,
                    "time": nome_time,
                    "logo": logo_url,
                    "pontos": int(pontos) if pontos.isdigit() else 0,
                    "jogos": jogos,
                    "vitorias": vitorias,
                    "empates": empates,
                    "derrotas": derrotas,
                    "saldo": saldo,
                })
    except Exception as e:
        print(f"Erro ao buscar classificação: {e}")

    # 2. Puxa as Partidas do dia (Scoreboard)
    try:
        resp_score = requests.get(url_scoreboard, timeout=10)
        if resp_score.status_code == 200:
            dados_sc = resp_score.json()
            eventos = dados_sc.get("events", [])

            for evento in eventos:
                competicao = evento.get("competitions", [{}])[0]
                competidores = competicao.get("competitors", [])

                if len(competidores) < 2:
                    continue

                mandante_obj = (
                    competidores[0]
                    if competidores[0].get("homeAway") == "home"
                    else competidores[1]
                )
                visitante_obj = (
                    competidores[1]
                    if competidores[1].get("homeAway") == "away"
                    else competidores[0]
                )

                time_casa = mandante_obj.get("team", {}).get("displayName", "Casa")
                time_fora = visitante_obj.get("team", {}).get("displayName", "Visitante")
                placar_casa = mandante_obj.get("score", "0")
                placar_fora = visitante_obj.get("score", "0")

                status_info = evento.get("status", {})
                status_type = status_info.get("type", {})
                
                tipo_status = status_type.get("name", "STATUS_SCHEDULED")
                estado_api = status_type.get("state", "")
                concluido_api = status_type.get("completed", False)

                horario_utc = evento.get("date", "")

                try:
                    dt_utc = datetime.strptime(horario_utc, "%Y-%m-%dT%H:%M%z")
                    dt_local = dt_utc - timedelta(hours=3)
                    horario_txt = dt_local.strftime("%H:%M")
                except Exception:
                    horario_txt = "16:00"

                gols = []
                amarelos = []
                vermelhos = []

                for detalhe in competicao.get("details", []):
                    tipo_lance = detalhe.get("type", {}).get("text", "").lower()
                    atleta = (
                        detalhe.get("athletes", [{}])[0].get("displayName", "Jogador")
                        if detalhe.get("athletes")
                        else ""
                    )
                    if "gol" in tipo_lance or "goal" in tipo_lance:
                        gols.append(
                            f"{atleta} ({detalhe.get('clock', {}).get('displayValue', '')})"
                        )
                    elif "amarelo" in tipo_lance or "yellow" in tipo_lance:
                        amarelos.append(atleta)
                    elif "vermelho" in tipo_lance or "red" in tipo_lance:
                        vermelhos.append(atleta)

                # --- BLINDAGEM DE STATUS CORRIGIDA ---
                if estado_api == "post" or concluido_api or tipo_status == "STATUS_FINAL":
                    status_final = "encerrado"
                elif estado_api == "in" or tipo_status == "STATUS_IN_PROGRESS":
                    status_final = "ao_vivo"
                elif estado_api == "pre" or tipo_status == "STATUS_SCHEDULED":
                    status_final = "agendado"
                else:
                    try:
                        agora = datetime.now()
                        hora_jogo = datetime.strptime(horario_txt, "%H:%M").time()
                        data_hora_jogo = datetime.combine(agora.date(), hora_jogo)
                        if agora >= (data_hora_jogo - timedelta(minutes=15)) and agora < (
                            data_hora_jogo + timedelta(hours=3)
                        ):
                            status_final = "ao_vivo"
                        elif agora >= (data_hora_jogo + timedelta(hours=3)):
                            status_final = "encerrado"
                        else:
                            status_final = "agendado"
                    except Exception:
                        status_final = "agendado"

                partidas[status_final].append({
                    "mandante": time_casa,
                    "visitante": time_fora,
                    "placar": f"{placar_casa} x {placar_fora}",
                    "horario": horario_txt,
                    "gols": gols,
                    "cartoes_amarelos": amarelos,
                    "cartoes_vermelhos": vermelhos,
                })
    except Exception as e:
        print(f"Erro ao buscar partidas: {e}")

    # Fallback se a tabela vier vazia
    if not tabela_completa:
        tabela_completa = [{
            "posicao": 1,
            "time": "Flamengo",
            "logo": "",
            "pontos": 0,
            "jogos": "0",
            "vitorias": "0",
            "empates": "0",
            "derrotas": "0",
            "saldo": "0",
        }]

    return {"partidas": partidas, "tabela_pontos": tabela_completa}
