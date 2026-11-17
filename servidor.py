from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
import os
from urllib.parse import parse_qs, urlparse
import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'dbname': 'geoprocessamento',
    'user': 'postgres',
    'password': '123',
}


def buscar_todos_locais():
  conn = psycopg2.connect(**DB_CONFIG)
  cur = conn.cursor()
  cur.execute('SELECT nome, ST_X(geom), ST_Y(geom) FROM locais;')
  dados = cur.fetchall()
  cur.close()
  conn.close()
  return [{'nome': row[0], 'lon': row[1], 'lat': row[2]} for row in dados]


def calcular_rota_entre(origem_nome, destino_nome):
  conn = psycopg2.connect(**DB_CONFIG)
  cur = conn.cursor()
  cur.execute(
      'SELECT nome, ST_X(geom), ST_Y(geom) FROM locais WHERE nome IN (%s,'
      ' %s);',
      (origem_nome, destino_nome),
  )
  dados = cur.fetchall()
  cur.close()
  conn.close()

  locais = {row[0]: {'lon': row[1], 'lat': row[2]} for row in dados}
  origem = locais.get(origem_nome)
  destino = locais.get(destino_nome)

  if not origem or not destino:
    return {'erro': 'Local de origem ou destino não encontrado no banco.'}

  lat1, lon1 = math.radians(origem['lat']), math.radians(origem['lon'])
  lat2, lon2 = math.radians(destino['lat']), math.radians(destino['lon'])

  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a = (
      math.sin(dlat / 2) ** 2
      + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
  )
  c = 2 * math.asin(math.sqrt(a))
  distancia_km = 6371 * c

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
      'origem_nome': origem_nome,
      'destino_nome': destino_nome,
      'origem': origem,
      'destino': destino,
      'distancia_km': round(distancia_km, 2),
      'estimativas': estimativas,
  }


class ServidorGeoHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    parsed_path = urlparse(self.path)
    path = parsed_path.path
    query_params = parse_qs(parsed_path.query)

    if path == '/api/locais':
      try:
        locais = buscar_todos_locais()
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(locais).encode('utf-8'))
      except Exception as e:
        self.send_response(500)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({'erro': str(e)}).encode('utf-8'))

    elif path == '/api/rota':
      try:
        origem = query_params.get('origem', [''])[0]
        destino = query_params.get('destino', [''])[0]
        resultado = calcular_rota_entre(origem, destino)

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

    elif path == '/' or path == '/index.html':
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
        self.wfile.write(b'Arquivo index.html nao encontrado.')
    else:
      self.send_response(404)
      self.end_headers()


if __name__ == '__main__':
  servidor = HTTPServer(('0.0.0.0', 8000), ServidorGeoHandler)
  print('Servidor rodando em http://0.0.0.0:8000')
  servidor.serve_forever()
