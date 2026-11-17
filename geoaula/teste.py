import psycopg

DSN = "host=localhost dbname=geoaula user=postgres password=1234"

with psycopg.connect(DSN) as conn:
     versao = conn.execute("SELECT postgis_version()").fetchone()
     print("conectado! PostGis:", versao[0])
