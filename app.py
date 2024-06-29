from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Conectando ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Para que possamos acessar as colunas por nome
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        nome = data.get('nome')
        email = data.get('email')
        evento = data.get('evento')
        filhos = data.get('filhos')
        idades = data.get('idades')

        # Conectando ao banco de dados e criando a tabela se não existir
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                evento TEXT NOT NULL,
                filhos TEXT,
                idades TEXT
            )
        ''')

        # Inserindo os dados na tabela
        conn.execute('''
            INSERT INTO responses (nome, email, evento, filhos, idades)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, email, evento, filhos, idades))

        conn.commit()
        conn.close()

        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
