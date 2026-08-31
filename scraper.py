from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup


def buscar_dados_serie_a():
  url = "https://ge.globo.com/futebol/brasileirao-serie-a/"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  partidas = {"ao_vivo": [], "agendado": [], "encerrado": []}
  tabela_pontos = {}

  try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")

      for jogo in soup.select(
          ".feed-ge-fixture__item, .jogo, [class*='partida']"
      ):
        try:
          time_casa = (
              jogo.select_one(".timaum-home, .team-home, [class*='home']")
              .get_text(strip=True)
              .split()[-1]
          )
          time_fora = (
              jogo.select_one(".timaum-away, .team-away, [class*='away']")
              .get_text(strip=True)
              .split()[-1]
          )
          placar_casa_txt = (
              jogo.select_one(".placar-home, [class*='score-home']")
              .get_text(strip=True)
              if jogo.select_one(
                  ".placar-home, [class*='score-home']"
              )
              else "0"
          )
          placar_fora_txt = (
              jogo.select_one(".placar-fora, [class*='score-away']")
              .get_text(strip=True)
              if jogo.select_one(
                  ".placar-fora, [class*='score-away']"
              )
              else "0"
          )

          status_txt = (
              jogo.select_one(
                  ".status-jogo, .match-status, [class*='status']"
              )
              .get_text(strip=True)
              .lower()
          )
          horario_txt = (
              jogo.select_one(".horario, .match-time, [class*='time']")
              .get_text(strip=True)
              if jogo.select_one(".horario, .match-time, [class*='time']")
              else "16:00"
          )

          gols = [
              g.get_text(strip=True)
              for g in jogo.select(".gol, .event-goal, [class*='goal']")
          ]
          amarelos = [
              a.get_text(strip=True)
              for a in jogo.select(
                  ".cartao-amarelo, .yellow-card, [class*='yellow']"
              )
          ]
          vermelhos = [
              v.get_text(strip=True)
              for v in jogo.select(
                  ".cartao-vermelho, .red-card, [class*='red']"
              )
          ]

          # Lógica de Status
          agora = datetime.now()
          status_final = "agendado"

          if any(
              x in status_txt
              for x in ["encerrado", "fim de jogo", "terminado"]
          ):
            status_final = "encerrado"
          elif any(
              x in status_txt
              for x in ["andamento", "intervalo", "ao vivo", "1º", "2º"]
          ):
            status_final = "ao_vivo"
          else:
            try:
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

          # Inicializa pontuação dos times se não existir
          for t in [time_casa, time_fora]:
            if t not in tabela_pontos:
              tabela_pontos[t] = 0

          # Se o jogo estiver encerrado, computa os pontos na tabela
          if status_final == "encerrado":
            try:
              pc = int(placar_casa_txt)
              pf = int(placar_fora_txt)
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
              "placar": f"{placar_casa_txt} x {placar_fora_txt}",
              "horario": horario_txt,
              "gols": gols,
              "cartoes_amarelos": amarelos,
              "cartoes_vermelhos": vermelhos,
          }

          partidas[status_final].append(dados_partida)

        except Exception:
          continue

  except Exception as e:
    print(f"Erro no scraper: {e}")

  # Ordena a tabela de pontos do maior para o menor
  tabela_ordenada = dict(
      sorted(tabela_pontos.items(), key=lambda item: item[1], reverse=True)
  )

  return {"partidas": partidas, "tabela_pontos": tabela_ordenada}