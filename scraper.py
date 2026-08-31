from datetime import datetime, timedelta
import requests


def buscar_dados_serie_a():
  # Endpoint oficial da ESPN para o Brasileirão Série A
  url = "https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard"

  partidas = {"ao_vivo": [], "agendado": [], "encerrado": []}
  tabela_pontos = {}

  try:
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
      return _fallback_dados()

    dados = response.json()
    eventos = dados.get("events", [])

    for evento in eventos:
      competicao = evento.get("competitions", [{}])[0]
      competidores = competicao.get("competitors", [])

      if len(competidores) < 2:
        continue

      # Identifica mandante e visitante
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

      # Status da partida na ESPN
      status_info = evento.get("status", {})
      tipo_status = status_info.get("type", {}).get("name", "STATUS_SCHEDULED")
      horario_utc = evento.get("date", "")

      # Converte horário UTC para o horário local do Brasil (-3h)
      try:
        dt_utc = datetime.strptime(horario_utc, "%Y-%m-%dT%H:%M%z")
        dt_local = dt_utc - timedelta(hours=3)
        horario_txt = dt_local.strftime("%H:%M")
      except Exception:
        horario_txt = "16:00"

      # Extração de detalhes (gols e cartões se disponíveis na API)
      gols = []
      amarelos = []
      vermelhos = []

      detalhes_jogadas = competicao.get("details", [])
      for detalhe in detalhes_jogadas:
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

      # Classificação por Status
      status_final = "agendado"
      if tipo_status == "STATUS_FINAL":
        status_final = "encerrado"
      elif tipo_status == "STATUS_IN_PROGRESS":
        status_final = "ao_vivo"
      else:
        # Regra dos 10 minutos antes do jogo
        try:
          agora = datetime.now()
          hora_jogo = datetime.strptime(horario_txt, "%H:%M").time()
          data_hora_jogo = datetime.combine(agora.date(), hora_jogo)
          limite_inicio = data_hora_jogo - timedelta(minutes=10)

          if agora >= limite_inicio and agora < data_hora_jogo + timedelta(
              hours=2
          ):
            status_final = "ao_vivo"
          elif agora >= data_hora_jogo + timedelta(hours=2):
            status_final = "encerrado"
          else:
            status_final = "agendado"
        except Exception:
          status_final = "agendado"

      # Inicializa pontos
      for t in [time_casa, time_fora]:
        if t not in tabela_pontos:
          tabela_pontos[t] = 0

      # Computa pontos se encerrado
      if status_final == "encerrado":
        try:
          pc = int(placar_casa)
          pf = int(placar_fora)
          if pc > pf:
            tabela_pontos[time_casa] += 3
          elif pf > pc:
            tabela_pontos[time_fora] += 3
          else:
            tabela_pontos[time_casa] += 1
            tabela_pontos[time_fora] += 1
        except Exception:
          pass

      dados_partida = {
          "mandante": time_casa,
          "visitante": time_fora,
          "placar": f"{placar_casa} x {placar_fora}",
          "horario": horario_txt,
          "gols": gols,
          "cartoes_amarelos": amarelos,
          "cartoes_vermelhos": vermelhos,
      }

      partidas[status_final].append(dados_partida)

  except Exception as e:
    print(f"Erro na API ESPN: {e}")
    return _fallback_dados()

  tabela_ordenada = dict(
      sorted(tabela_pontos.items(), key=lambda item: item[1], reverse=True)
  )
  return {"partidas": partidas, "tabela_pontos": tabela_ordenada}


def _fallback_dados():
  return {
      "partidas": {
          "ao_vivo": [],
          "agendado": [{
              "mandante": "Flamengo",
              "visitante": "Palmeiras",
              "placar": "0 x 0",
              "horario": "16:00",
              "gols": [],
              "cartoes_amarelos": [],
              "cartoes_vermelhos": [],
          }],
          "encerrado": [],
      },
      "tabela_pontos": {"Flamengo": 0, "Palmeiras": 0},
  }
