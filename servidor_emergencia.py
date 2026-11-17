from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from datetime import datetime
from urllib.parse import urlparse

ARQUIVO_DADOS = "dados.json"

# Dados padrão caso o arquivo ainda não exista
DADOS_INICIAIS = {
    "bombeiros": [
        {"nome": "Quartel Central de Bombeiros", "rua": "Rua Principal", "referencia": "Próximo à Praça Central", "lat": -6.075421, "lon": -49.884724},
        {"nome": "Base Avançada 23° Batalhão", "rua": "Av. dos Ipês", "referencia": "Esquina com o Ginásio", "lat": -6.071065, "lon": -49.900138}
    ],
    "hospitais": [
        {"nome": "Hospital Municipal de Parauapebas", "leitos": 120, "rua": "Rua F", "referencia": "Perto do Bairro Cidade Nova", "lat": -6.062862, "lon": -49.909038},
        {"nome": "Hospital Geral de Parauapebas - HGP", "leitos": 80, "rua": "Rodovia PA-275", "referencia": "Área Institucional", "lat": -6.062449, "lon": -49.909876},
        {"nome": "UPA 24H", "leitos": 80, "rua": "Av. Principal", "referencia": "Próximo ao Posto Fiscal", "lat": -6.083129, "lon": -49.851315}
    ],
    "ocorrencias": [
        {"id": 1, "descricao": "Edificação com danos estruturais - Bairro Tropical", "severidade": "Alta", "lat": -6.026349, "lon": -49.888576, "horario": "16/11/2026 21:00", "rua": "Rua das Palmeiras", "referencia": "Próximo ao mercado local"},
        {"id": 2, "descricao": "Deslizamento - Bairro São Lucas II", "severidade": "Crítica", "lat": -6.108045, "lon": -49.898670, "horario": "16/11/2026 21:15", "rua": "Rua do Sol", "referencia": "Área de encosta"},
        {"id": 3, "descricao": "Acidente - Bairro Serra Grande", "severidade": "Moderado", "lat": -6.055461, "lon": -49.846358, "horario": "16/11/2026 21:30", "rua": "Av Maringá", "referencia": "Cruzamento principal"}
    ]
}

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    salvar_dados(DADOS_INICIAIS)
    return DADOS_INICIAIS

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

class ServidorEmergenciaHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/emergencia':
            dados_atuais = carregar_dados()
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(dados_atuais, ensure_ascii=False).encode('utf-8'))
        elif path in ('/', '/login.html'):
            self.enviar_arquivo('login.html')
        elif path == '/emergencia.html':
            self.enviar_arquivo('emergencia.html')
        elif path == '/cadastro.html':
            self.enviar_arquivo('cadastro.html')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            dados_req = json.loads(body.decode('utf-8'))
            dados_sistema = carregar_dados()

            if parsed.path == '/api/adicionar':
                novo_id = max([o["id"] for o in dados_sistema["ocorrencias"]], default=0) + 1
                horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                nova_ocorrencia = {
                    "id": novo_id,
                    "descricao": dados_req.get("descricao"),
                    "severidade": dados_req.get("severidade"),
                    "lat": float(dados_req.get("lat")),
                    "lon": float(dados_req.get("lon")),
                    "horario": dados_req.get("horario") or horario_atual,
                    "rua": dados_req.get("rua", ""),
                    "referencia": dados_req.get("referencia", "")
                }
                dados_sistema["ocorrencias"].append(nova_ocorrencia)
                salvar_dados(dados_sistema)
                self.enviar_json({"status": "sucesso"})

            elif parsed.path == '/api/remover':
                oc_id = int(dados_req.get("id"))
                dados_sistema["ocorrencias"] = [o for o in dados_sistema["ocorrencias"] if o["id"] != oc_id]
                salvar_dados(dados_sistema)
                self.enviar_json({"status": "sucesso"})
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "erro", "mensagem": str(e)}).encode('utf-8'))

    def enviar_json(self, dados):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(dados, ensure_ascii=False).encode('utf-8'))

    def enviar_arquivo(self, nome):
        try:
            caminho = os.path.join(os.path.dirname(__file__), nome)
            with open(caminho, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(f.read())
        except:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    servidor = HTTPServer(('0.0.0.0', 8001), ServidorEmergenciaHandler)
    print("Servidor de Emergencia com Persistência rodando em http://0.0.0.0:8001")
    servidor.serve_forever()
