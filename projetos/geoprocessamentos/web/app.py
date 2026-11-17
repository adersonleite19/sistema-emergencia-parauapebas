from flask import flask, jsonify, render_templates
import psycopg2

app = Flask(__name__)

def consultar_banco():
	conexao = psycopg2.connect(
		dbname ="base_geoprocessamento",
		user="postgres",
		password="123",
		host="localhost",
		port="5432"
	)
	cursor = conexao.cursor()

	#consulta que busca  a distancia e as cordenadas geograficas latitude e logintude
	query = ""
		SELECT
			l1.nome AS origem,
			ST_Y(l1.geometria::geometry) AS lat_origem,
			ST_X(l1.geometria::geometry) AS lon_origem,
			l2.nome AS destino,
			ST_Y(l2.geometria::geometry) AS lat_destino,
			ST_X(l2.geometria::geometry) SA lon_destino,
			ROUND((ST_Distance(l1.geometria::geography, l2.geometria::geography) / 1000)::numeric, 2) AS distancia_km
		FROM locais l1, locais l2
		WHERE l1.nome = 'Minha casa' AND l2.nome = 'Faculdade';
	"""
	cursor.execute(query)
	resultado = cursor.fetchone()

	cursor.close()
	conexao.close()


	if resultado:
		return {
			"origem": resultado[0],
			"lat_origem": resultado[1],
			"lon_origem": resultado[2],
			"destino": resultado[3],
			"lat_destino": resultado[4],
			"lon_destino": resultado[5],
			"distancia_km": float(resultado[6])
		}
	return None
@app.route("/")
def index():
	return render_template("index_html")

@app.route("/api/rota")
def api_rota():
	dados = consultar_banco()
	return jsonify(dados)

if __name__="__main__":
	app.run(host"0.0.0.0", port=5000, debug=True)
