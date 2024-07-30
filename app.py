from flask import Flask, render_template, request, jsonify, send_file
from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData
from sqlalchemy.orm import sessionmaker
import pandas as pd
import io
import os

app = Flask(__name__)

# Configuração do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Definindo a tabela usando SQLAlchemy
responses = Table(
    'responses', metadata,
    Column('id', Integer, primary_key=True),
    Column('nome', String, nullable=False),
    Column('email', String, nullable=False),
    Column('evento', String, nullable=False),
    Column('filhos', String),
    Column('idades', String)
)

metadata.create_all(engine)
Session = sessionmaker(bind=engine)

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

        session = Session()
        session.execute(
            responses.insert().values(
                nome=nome,
                email=email,
                evento=evento,
                filhos=filhos,
                idades=idades
            )
        )
        session.commit()
        session.close()

        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/export_to_excel')
def export_to_excel():
    try:
        session = Session()
        query = session.query(responses).all()
        session.close()

        # Converting query result to DataFrame
        df = pd.DataFrame([dict(row) for row in query])

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
