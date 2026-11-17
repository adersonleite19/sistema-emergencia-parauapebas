import psycopg2

def calcular_rota():
	try:
		conexao = psycopg2.connect(
			dbname="base_geoprocessamento",
			user="postgres",
			password="123",
			host="localhost",
			port="5432"
		)

		cursor = conexao.cursor()

		#recria tabela limpa
		cursor.execute("DROP TABLE IF EXISTS locais;")
		cursor.execute("""
			CREATE TABLE locais (
				id SERIAL PRIMARY KEY,
				nome VARCHAR(100),
				tipo VARCHAR(50),
				geometria GEOMETRY(Point, 4326)
			);
		""")

		#insere pontos de casa a faculdade
		cursor.execute("""
			INSERT INTO locais (nome, tipo, geometria) VALUES
			('Minha casa', 'residencia', ST_GeomFromText('POINT(-46.633309 -23.550520)', 4326)),
			('Faculdade', 'educacao', ST_GeomFromText('POINT(-46.6555290 -23.561684)', 4326));
		""")
		
		#CONSULTA A DISTANCIA ENTRE PONTOS UTILIZANDO POSTGIS
		query = """
			SELECT
				l1.nome AS origem,
				l2.nome AS destino,
				ROUND((ST_Distance(l1.geometria::geography, l2.geometria::geography) / 1000)::numeric, 2) AS distancia_km
			FROM locais l1, locais l2
			WHERE l1.nome = 'Minha casa' AND l2.nome = 'Faculdade';
		"""
		
		cursor.execute(query)
		resultado = cursor.fetchone()

		if resultado:
			print(f"Origem: {resultado[0]}")
			print(f"Destino: {resultado[1]}")
			print(f"Distancia calculada: {resultado[2]} km")

		conexao.commit()
		cursor.close()
		conexao.close()

	except Exception as erro:
		print(f"Erro ao conectar ou executar no banco: {erro}")

if __name__ == "__main__":
	calcular_rota()
