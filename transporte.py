import math
import psycopg2

# Conexão com o PostgreSQL
try:
  conn = psycopg2.connect(
      dbname='geoprocessamento', user='postgres', password='1234'
  )
  cur = conn.cursor()

  # Consulta para pegar as coordenadas da Faculdade e da Casa
  cur.execute(
      "SELECT nome, ST_X(geom), ST_Y(geom) FROM locais WHERE nome IN"
      " ('Faculdade', 'Casa');"
  )
  dados = cur.fetchall()

  locais = {row[0]: (row[1], row[2]) for row in dados}
  faculdade = locais.get('Faculdade')
  casa = locais.get('Casa')

  if not faculdade or not casa:
    print(
        'Erro: Locais não encontrados no banco de dados. Verifique a inserção.'
    )
    exit()

  # Cálculo de distância geodésica aproximada (Haversine) em quilômetros
  lat1, lon1 = math.radians(faculdade[1]), math.radians(faculdade[0])
  lat2, lon2 = math.radians(casa[1]), math.radians(casa[0])

  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a = (
      math.sin(dlat / 2) ** 2
      + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
  )
  c = 2 * math.asin(math.sqrt(a))
  distancia_km = 6371 * c  # raio médio da Terra em km

  print('=== SISTEMA DE ROTA E GEOPROCESSAMENTO (TERMINAL) ===')
  print(f'Distância vetorial entre a Faculdade e a Casa: {distancia_km:.2f} km\n')

  # Estimativa de tempo para cada modal de transporte solicitado
  # Velocidades médias aproximadas (km/h)
  modais = {
      'Pessoa a pé': 5,
      'Bicicleta': 15,
      'Moto': 40,
      'Carro': 30,
      'Avião': 300,  # para fins de simulação de rota aérea direta
  }

  print('Estimativa de tempo por modal de transporte:')
  for modal, velocidade in modais.items():
    tempo_horas = distancia_km / velocidade
    tempo_minutos = tempo_horas * 60
    print(
        f'- {modal}: {tempo_minutos:.1f} minutos (Velocidade média:'
        f' {velocidade} km/h)'
    )

  cur.close()
  conn.close()

except Exception as e:
  print(f'Erro ao conectar ou executar no banco de dados: {e}')
