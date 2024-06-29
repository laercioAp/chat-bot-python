from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json

    # Transformar o dicionário de respostas em uma linha de DataFrame
    responses = {question: [answer] for question, answer in data.items()}
    df = pd.DataFrame(responses)

    # Verificar se o arquivo Excel existe
    file_path = 'responses.xlsx'
    if os.path.exists(file_path):
        # Se o arquivo existe, carregar o DataFrame existente
        existing_df = pd.read_excel(file_path)
        # Concatenar o novo DataFrame ao existente
        df = pd.concat([existing_df, df], ignore_index=True)
    else:
        # Se o arquivo não existe, criar um novo DataFrame com as respostas
        df.to_excel(file_path, index=False)

    # Salvar o DataFrame atualizado de volta no arquivo Excel
    df.to_excel(file_path, index=False)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run()
