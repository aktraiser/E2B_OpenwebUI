from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import base64
import pandas as pd
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
from anthropic import Anthropic

load_dotenv()

app = Flask(__name__)
CORS(app)

def generate_analysis_code(csv_path, analysis_request, csv_structure):
    """Génère directement le code d'analyse Python sans passer par Claude"""
    
    code_template = f'''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuration matplotlib pour charts interactifs
plt.style.use('default')
plt.rcParams['figure.figsize'] = (12, 8)

# Charger les données
df = pd.read_csv('dataset.csv')

print("=== ANALYSE AUTOMATIQUE DES DONNÉES ===")
print(f"Dataset shape: {{df.shape}}")
print(f"Colonnes: {{list(df.columns)}}")
print()

# 1. STATISTIQUES DESCRIPTIVES
print("1. STATISTIQUES DESCRIPTIVES")
print("-" * 40)
print(df.describe())
print()

# 2. ANALYSE TEMPORELLE (si colonne date existe)
date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
if date_cols:
    date_col = date_cols[0]
    df[date_col] = pd.to_datetime(df[date_col])
    
    print(f"2. ÉVOLUTION TEMPORELLE - {{date_col}}")
    print("-" * 40)
    
    # Graphique temporel pour chaque métrique numérique
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Évolution Temporelle des Métriques Clés', fontsize=16)
    
    for i, col in enumerate(numeric_cols[:4]):
        ax = axes[i//2, i%2]
        if 'product' in df.columns:
            for product in df['product'].unique():
                product_data = df[df['product'] == product]
                monthly_data = product_data.groupby(date_col)[col].sum()
                ax.plot(monthly_data.index, monthly_data.values, marker='o', label=product)
        else:
            monthly_data = df.groupby(date_col)[col].sum()
            ax.plot(monthly_data.index, monthly_data.values, marker='o')
        
        ax.set_title(f'Évolution {{col}}')
        ax.set_xlabel('Date')
        ax.set_ylabel(col)
        ax.legend()
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()

# 3. COMPARAISON PAR CATÉGORIES
categorical_cols = df.select_dtypes(include=['object']).columns
categorical_cols = [col for col in categorical_cols if col not in date_cols]

if len(categorical_cols) > 0:
    cat_col = categorical_cols[0]  # Première colonne catégorielle
    
    print(f"3. ANALYSE PAR {{cat_col.upper()}}")
    print("-" * 40)
    
    # Graphique comparatif
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Revenus par catégorie
    revenue_cols = [col for col in numeric_cols if 'revenue' in col.lower() or 'sales' in col.lower()]
    if revenue_cols:
        revenue_col = revenue_cols[0]
        category_revenue = df.groupby(cat_col)[revenue_col].sum()
        
        axes[0].bar(category_revenue.index, category_revenue.values, color=['#2E86AB', '#A23B72', '#F18F01'])
        axes[0].set_title(f'{{revenue_col}} total par {{cat_col}}')
        axes[0].set_ylabel(revenue_col)
        
        # Performance temporelle par catégorie
        if date_cols:
            pivot_data = df.pivot_table(values=revenue_col, index=date_col, columns=cat_col, aggfunc='sum')
            pivot_data.plot(kind='line', ax=axes[1], marker='o')
            axes[1].set_title(f'Évolution {{revenue_col}} par {{cat_col}}')
            axes[1].set_ylabel(revenue_col)
    
    plt.tight_layout()
    plt.show()

# 4. ANALYSE DE CORRÉLATION
if len(numeric_cols) > 1:
    print("4. MATRICE DE CORRÉLATION")
    print("-" * 40)
    
    corr_matrix = df[numeric_cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                square=True, fmt='.2f', cbar_kws={{"shrink": .8}})
    plt.title('Matrice de Corrélation entre Variables')
    plt.tight_layout()
    plt.show()
    
    # Insights de corrélation
    strong_corr = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_val = corr_matrix.iloc[i,j]
            if abs(corr_val) > 0.7:
                strong_corr.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
    
    if strong_corr:
        print("Corrélations fortes détectées:")
        for col1, col2, corr in strong_corr:
            print(f"  - {{col1}} ↔ {{col2}}: {{corr:.3f}}")

# 5. INSIGHTS AUTOMATIQUES
print()
print("5. INSIGHTS CLÉS")
print("-" * 40)

# Calcul des insights
insights = []

# Croissance
if date_cols and revenue_cols:
    first_period = df[df[date_col] == df[date_col].min()][revenue_cols[0]].sum()
    last_period = df[df[date_col] == df[date_col].max()][revenue_cols[0]].sum()
    growth = ((last_period - first_period) / first_period) * 100
    insights.append(f"Croissance revenue: {{growth:.1f}}% sur la période")

# Performance par catégorie
if categorical_cols and revenue_cols:
    best_category = df.groupby(categorical_cols[0])[revenue_cols[0]].sum().idxmax()
    insights.append(f"Meilleure performance: {{best_category}}")

# Tendances
if len(numeric_cols) >= 2:
    col1, col2 = numeric_cols[0], numeric_cols[1]
    trend_corr = df[col1].corr(df[col2])
    if abs(trend_corr) > 0.5:
        insights.append(f"Corrélation {{trend_corr:.2f}} entre {{col1}} et {{col2}}")

for insight in insights:
    print(f"✓ {{insight}}")

print()
print("=== ANALYSE TERMINÉE ===")
'''
    
    return code_template

def analyze_csv_with_guaranteed_results(csv_path_in_sandbox, analysis_request):
    """Analyse garantie avec génération automatique de code"""
    
    # 1. Analyser la structure du CSV
    df = pd.read_csv(csv_path_in_sandbox)
    csv_structure = {
        "columns": list(df.columns),
        "shape": list(df.shape),
        "dtypes": {k: str(v) for k, v in df.dtypes.to_dict().items()},
        "sample": df.head(3).astype(str).to_dict()
    }
    
    # 2. Générer le code d'analyse approprié
    analysis_code = generate_analysis_code(csv_path_in_sandbox, analysis_request, csv_structure)
    
    # 3. Exécuter dans E2B
    sbx = Sandbox.create()
    
    try:
        # Upload du CSV
        with open(csv_path_in_sandbox, "rb") as f:
            sbx.files.write("dataset.csv", f)
        
        # Exécution du code d'analyse
        execution = sbx.run_code(analysis_code)
        
        results = []
        
        if execution.error:
            results.append({
                "type": "error",
                "error": {
                    "name": execution.error.name,
                    "value": execution.error.value,
                    "traceback": execution.error.traceback
                }
            })
        else:
            # Traiter tous les résultats
            for result in execution.results:
                if result.chart:
                    # Chart interactif E2B
                    chart_data = {
                        "type": "interactive_chart",
                        "chart_type": getattr(result.chart, 'type', 'unknown'),
                        "title": getattr(result.chart, 'title', 'Chart'),
                        "x_label": getattr(result.chart, 'x_label', None),
                        "y_label": getattr(result.chart, 'y_label', None),
                        "elements": []
                    }
                    
                    if hasattr(result.chart, 'elements'):
                        for element in result.chart.elements:
                            chart_data["elements"].append({
                                "label": getattr(element, 'label', ''),
                                "value": getattr(element, 'value', 0),
                                "group": getattr(element, 'group', '')
                            })
                    
                    results.append(chart_data)
                
                elif result.png:
                    # Chart statique PNG
                    results.append({
                        "type": "static_chart",
                        "png_base64": result.png
                    })
                
                elif result.text:
                    # Sortie texte
                    results.append({
                        "type": "text",
                        "content": result.text
                    })
        
        # 4. Ajouter résumé de la structure des données
        results.insert(0, {
            "type": "dataset_info",
            "structure": csv_structure,
            "analysis_type": "comprehensive_automated"
        })
        
        return results
        
    finally:
        sbx.kill()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'csv_file' not in request.files:
            return jsonify({"error": "No CSV file provided"}), 400
        
        csv_file = request.files['csv_file']
        if csv_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        analysis_request = request.form.get('analysis_request', 'Analyze this dataset comprehensively')
        
        # Sauvegarder temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            csv_file.save(temp_file.name)
            temp_csv_path = temp_file.name
        
        try:
            # Analyse garantie
            results = analyze_csv_with_guaranteed_results(temp_csv_path, analysis_request)
            
            return jsonify({
                "success": True,
                "results": results,
                "analysis_guaranteed": True
            })
        
        finally:
            if os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)