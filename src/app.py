from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import numpy as np 

app = Flask(__name__)
CORS(app, origins=["https://projeto-python-facul.vercel.app", "http://localhost:8080", "http://127.0.0.1:8080"])

# --- CARREGAMENTO E PREPARAÇÃO DO CSV ---
CSV_FILE = 'br_ibge_censo_2022_municipio.csv'
try:
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CSV_FILE)
    df = pd.read_csv(csv_path, dtype={'id_municipio': str, 'sigla_uf': str})
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    df = df[df['populacao'] > 0].copy()
except Exception as e:
    print(f"Erro crítico ao carregar o CSV: {e}")
    df = pd.DataFrame()


def save_csv():
    if not df.empty:
        try:
            df.to_csv(csv_path, index=False)
            print("CSV salvo com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar CSV: {e}")
            raise


@app.route("/")
def home():
    return "API do Censo 2022 - Versão Gráficos - Rodando..."
@app.route('/api/population_by_uf', methods=['GET'])
def get_population_by_uf():
    if df.empty: return jsonify({'error': 'Dados não carregados'}), 500
    pop_by_uf = df.groupby('sigla_uf')['populacao'].sum().reset_index().sort_values(by='populacao', ascending=False)
    return jsonify(pop_by_uf.to_dict(orient='records'))


@app.route('/api/estado/<uf>', methods=['PUT'])
def update_estado_data(uf):
    global df
    if df.empty: return jsonify({'error': 'Dados não carregados'}), 500
    uf = uf.upper()
    data = request.get_json()
    estado_indices = df[df['sigla_uf'] == uf].index
    if estado_indices.empty: return jsonify({'error': f'Estado {uf} não encontrado'}), 404
    update_fields = [
        'populacao', 'area', 'domicilios', 'populacao_indigena', 'populacao_quilombola',
        'taxa_alfabetizacao', 'idade_mediana', 'indice_envelhecimento', 'razao_sexo'
    ]
    if not data or not any(field in data for field in update_fields):
        return jsonify({'error': 'Requisição inválida.'}), 400
    num_municipios = len(estado_indices)
    if num_municipios > 0:
        for field in update_fields:
            if field in data:
                try:
                    total_value = float(data[field])
                    if field in ['taxa_alfabetizacao', 'idade_mediana', 'indice_envelhecimento', 'razao_sexo']:
                        df.loc[estado_indices, field] = total_value
                    else:
                        df.loc[estado_indices, field] = total_value / num_municipios
                except (ValueError, TypeError):
                    return jsonify({'error': f'Valor inválido para o campo {field}.'}), 400
        save_csv()
        return jsonify({'message': f'Dados de {uf} atualizados.'}), 200
    else:
        return jsonify({'error': 'Nenhum município para a UF'}), 404
    

@app.route('/api/estado/<uf>', methods=['DELETE'])
def delete_estado_data(uf):
    global df
    if df.empty: return jsonify({'error': 'Dados não carregados'}), 500
    uf = uf.upper()
    if df[df['sigla_uf'] == uf].empty: return jsonify({'error': f'Estado {uf} não encontrado'}), 404
    df.drop(df[df['sigla_uf'] == uf].index, inplace=True)
    save_csv()
    return jsonify({'message': f'Dados de {uf} deletados.'}), 200


@app.route('/api/estado/<uf>', methods=['GET'])
def get_estado_data(uf):
    if df.empty: return jsonify({'error': 'Dados não carregados'}), 500
    uf = uf.upper()
    estado_df = df[df['sigla_uf'] == uf]
    if estado_df.empty: return jsonify({'error': f'Estado {uf} não encontrado'}), 404
    populacao = int(estado_df['populacao'].sum())
    area = float(estado_df['area'].sum())
    domicilios = int(estado_df['domicilios'].sum())
    densidade_demografica = round(populacao / area, 2) if area > 0 else 0
    media_moradores_domicilio = round(populacao / domicilios, 2) if domicilios > 0 else 0
    data = {
        'populacao': populacao, 'area': area, 'domicilios': domicilios,
        'populacao_indigena': int(estado_df['populacao_indigena'].sum()),
        'populacao_quilombola': int(estado_df['populacao_quilombola'].sum()),
        'taxa_alfabetizacao': round(estado_df['taxa_alfabetizacao'].mean(), 2),
        'idade_mediana': round(estado_df['idade_mediana'].mean(), 2),
        'indice_envelhecimento': round(estado_df['indice_envelhecimento'].mean(), 2),
        'razao_sexo': round(estado_df['razao_sexo'].mean(), 2),
        'densidade_demografica': densidade_demografica,
        'media_moradores_domicilio': media_moradores_domicilio
    }
    return jsonify(data)


@app.route('/api/rankings', methods=['GET'])
def get_rankings_data():
    """Calcula e retorna rankings e insights nacionais."""
    if df.empty: return jsonify({'error': 'Dados não carregados'}), 500

    agregados = {
        'populacao': df.groupby('sigla_uf')['populacao'].sum(),
        'taxa_alfabetizacao': df.groupby('sigla_uf')['taxa_alfabetizacao'].mean(),
        'indice_envelhecimento': df.groupby('sigla_uf')['indice_envelhecimento'].mean()
    }
    
    df_estados = pd.DataFrame(agregados)

    
    rankings = {
        'alfabetizacao_top5': df_estados.nlargest(5, 'taxa_alfabetizacao')['taxa_alfabetizacao'].to_dict(),
        'alfabetizacao_bottom5': df_estados.nsmallest(5, 'taxa_alfabetizacao')['taxa_alfabetizacao'].to_dict(),
        'envelhecimento_top5': df_estados.nlargest(5, 'indice_envelhecimento')['indice_envelhecimento'].to_dict(),
        'envelhecimento_bottom5_mais_jovens': df_estados.nsmallest(5, 'indice_envelhecimento')['indice_envelhecimento'].to_dict(),
        'populacao_top5': df_estados.nlargest(5, 'populacao')['populacao'].to_dict(),
        'populacao_total': int(df['populacao'].sum())
    }

    return jsonify(rankings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)