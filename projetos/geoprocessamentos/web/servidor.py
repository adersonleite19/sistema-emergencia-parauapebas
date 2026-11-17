from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
import os
import psycopg2

# Configurações do Banco de Dados (ajuste a senha se necessário)
DB_CONFIG = {
    'host': 'localhost',
    'dbname': 'geoprocessamento',
    'user': 'postgres',
    'password': '123',
}


def calcular_dados_geoprocessamento():
  conn = psycopg2.connect(**DB_CONFIG)
  cur = conn.cursor()

  # Busca as coordenadas (longitude = ST_X, latitude = ST_Y)
  cur.execute(
      "SELECT nome, ST_X(geom), ST_Y(geom) FROM locais WHERE nome IN"
      " ('Faculdade', 'Casa');"
  )
  dados = cur.fetchall()

  cur.close()
  conn.close()

  locais = {row[0]: {'lon': row[1], 'lat': row[2]} for row in dados}
  faculdade = locais.get('Faculdade')
  casa = locais.get('Casa')

  if not faculdade or not casa:
    return {'erro': 'Locais Faculdade ou Casa não encontrados no banco.'}

  # Cálculo de distância (Haversine)
  lat1, lon1 = math.radians(faculdade['lat']), math.radians(faculdade['lon'])
  lat2, lon2 = math.radians(casa['lat']), math.radians(casa['lon'])

  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a = (
      math.sin(dlat / 2) ** 2
      + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
  )
  c = 2 * math.asin(math.sqrt(a))
  distancia_km = 6371 * c

  # Cálculo de tempo por modal
  modais = {
      'Pessoa a pé': 5,
      'Bicicleta': 15,
      'Moto': 40,
      'Carro': 30,
      'Avião': 300,
  }

  estimativas = []
  for modal, velocidade in modais.items():
    tempo_minutos = (distancia_km / velocidade) * 60
    estimativas.append({
        'modal': modal,
        'velocidade': velocidade,
        'minutos': round(tempo_minutos, 1),
    })

  return {
      'faculdade': faculdade,
      'casa': casa,
      'distancia_km': round(distancia_km, 2),
      'estimativas': estimativas,
  }


class ServidorGeoHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    # Rota da API que entrega os dados do PostGIS em JSON
    if self.path == '/api/rota':
      try:
        resultado = calcular_dados_geoprocessamento()
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(resultado).encode('utf-8'))
      except Exception as e:
        self.send_response(500)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({'erro': str(e)}).encode('utf-8'))

    # Rota principal que entrega a página HTML
    elif self.path == '/' or self.path == '/index.html':
      try:
        caminho_html = os.path.join(os.path.dirname(__file__), 'index.html')
        with open(caminho_html, 'rb') as f:
          conteudo = f.read()
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(conteudo)
      except FileNotFoundError:
        self.send_response(404)
        self.end_headers()
        self.wfile.write(
            b'Arquivo index.html nao encontrado na mesma pasta do servidor.py'
        )
    else:
      self.send_response(404)
      self.end_headers()


if __name__ == '__main__':
  # 0.0.0.0 permite acessar tanto pelo Ubuntu quanto pelo navegador do Windows via IP da VM
  servidor = HTTPServer(('0.0.0.0', 8000), ServidorGeoHandler)
  print('Servidor rodando! Acesse no navegador: http://192.168.1.8:8000')
  servidor.serve_forever()
