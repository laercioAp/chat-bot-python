from flask import Flask, render_template, request, jsonify, send_file
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import io
import os
from dotenv import load_dotenv

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

app = Flask(__name__)

# Configuração do Firebase
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS')
cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

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

        doc_ref = db.collection('responses').document()
        doc_ref.set({
            'nome': nome,
            'email': email,
            'evento': evento,
            'filhos': filhos,
            'idades': idades
        })

        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/export_to_excel')
def export_to_excel():
    try:
        responses_ref = db.collection('responses')
        docs = responses_ref.stream()

        # Convertendo documentos do Firestore para uma lista de dicionários
        responses_list = []
        for doc in docs:
            responses_list.append(doc.to_dict())

        # Convertendo lista de dicionários para DataFrame
        df = pd.DataFrame(responses_list)

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
