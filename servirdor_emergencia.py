
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from urllib.parse import urlparse
import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'dbname': 'geoprocessamento',
    'user': 'postgres',
    'password': '123',
}


def buscar_dados_emergencia():
  conn = psycopg2.connect(**DB_CONFIG)
  cur = conn.cursor()

  cur.execute('SELECT nome, ST_X(geom), ST_Y(geom) FROM bombeiros;')
  bombeiros = [
      {'nome': r[0], 'lon': r[1], 'lat': r[2]} for r in cur.fetchall()
  ]

  cur.execute('SELECT nome, leitos, ST_X(geom), ST_Y(geom) FROM hospitais;')
  hospitais = [
      {'nome': r[0], 'leitos': r[1], 'lon': r[2], 'lat': r[3]}
      for r in cur.fetchall()
  ]

  cur.execute(
      'SELECT id, descricao, severidade, ST_X(geom), ST_Y(geom) FROM'
      ' sismo_afetados;'
  )
  ocorrencias = [
      {
          'id': r[0],
          'descricao': r[1],
          'severidade': r[2],
          'lon': r[3],
          'lat': r[4],
      }
      for r in cur.fetchall()
  ]

  cur.close()
  conn.close()

  return {
      'bombeiros': bombeiros,
      'hospitais': hospitais,
      'ocorrencias': ocorrencias,
  }


class ServidorEmergenciaHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    parsed_path = urlparse(self.path)
    path = parsed_path.path

    if path == '/api/emergencia':
      try:
        dados = buscar_dados_emergencia()
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(dados).encode('utf-8'))
      except Exception as e:
        self.send_response(500)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({'erro': str(e)}).encode('utf-8'))

    elif path == '/' or path == '/emergencia.html':
      try:
        caminho_html = os.path.join(os.path.dirname(__file__), 'emergencia.html')
        with open(caminho_html, 'rb') as f:
          conteudo = f.read()
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(conteudo)
      except FileNotFoundError:
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Arquivo emergencia.html nao encontrado.')
    else:
      self.send_response(404)
      self.end_headers()


if __name__ == '__main__':
  servidor = HTTPServer(('0.0.0.0', 8001), ServidorEmergenciaHandler)
  print('Servidor de Emergencia rodando em http://0.0.0.0:8001')
  servidor.serve_forever()
