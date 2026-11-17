from flask import Flask, jsonify
import psycopg

app = Flask(__name__)
DSN = "host=127.0.0.1 dbname=indigena user=postgres password=12345"

@app.route("/")
def home():
    return jsonify({"status": "Servidor rodando!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000, debug=True)

