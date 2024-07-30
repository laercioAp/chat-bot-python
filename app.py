from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import pandas as pd
import io

app = Flask(__name__)

# Conectando ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db', timeout=10)  # Adiciona timeout para evitar "database is locked"
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

        if not nome or not email or not evento:
            return jsonify({'status': 'error', 'message': 'Campos obrigatórios não preenchidos'}), 400

        # Conectando ao banco de dados e criando a tabela se não existir
        conn = get_db_connection()
        with conn:  # Usa o contexto de gerenciamento para garantir o fechamento da conexão
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

        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/export_to_excel')
def export_to_excel():
    try:
        conn = get_db_connection()
        query = 'SELECT * FROM responses'
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Respostas')
        output.seek(0)

        return send_file(output, 
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, 
                         download_name='respostas.xlsx')
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
