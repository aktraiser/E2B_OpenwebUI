"""
Exécuteur pour le sandbox E2B
Le code d'analyse s'exécute ici, PAS CrewAI !
CrewAI tourne sur le VPS et envoie du code ici.
"""

from e2b_code_interpreter import Sandbox
import os

def execute_analysis_code(code: str, csv_data: str = None) -> dict:
    """
    Exécute du code d'analyse dans le sandbox E2B
    
    Args:
        code: Code Python à exécuter
        csv_data: Données CSV optionnelles
        
    Returns:
        Résultats de l'exécution
    """
    with Sandbox.create() as sandbox:
        # Upload CSV si fourni
        if csv_data:
            sandbox.files.write('dataset.csv', csv_data)
        
        # Exécuter le code
        execution = sandbox.run_code(code)
        
        # Formater les résultats
        results = {
            'success': not execution.error,
            'output': execution.text if execution.text else "",
            'results': []
        }
        
        if execution.error:
            results['error'] = {
                'name': execution.error.name,
                'value': execution.error.value,
                'traceback': execution.error.traceback
            }
        
        # Collecter les résultats (graphiques, données)
        if hasattr(execution, 'results') and execution.results:
            for result in execution.results:
                # Méthode 1: Utiliser _repr_png_ pour les images matplotlib/seaborn
                if hasattr(result, '_repr_png_'):
                    png_data = result._repr_png_()
                    if png_data:
                        results['results'].append({
                            'type': 'image',
                            'format': 'png',
                            'data': png_data  # Déjà en base64 selon la doc E2B
                        })
                # Méthode 2: Accès direct à l'attribut png si présent
                elif hasattr(result, 'png') and result.png:
                    import base64
                    results['results'].append({
                        'type': 'image', 
                        'format': 'png',
                        'data': base64.b64encode(result.png).decode('utf-8')
                    })
                # Méthode 3: Gérer les graphiques interactifs E2B
                elif hasattr(result, 'chart') and result.chart:
                    chart_data = {
                        'type': 'chart',
                        'chart_type': str(getattr(result.chart, 'type', 'UNKNOWN')),
                        'title': getattr(result.chart, 'title', ''),
                        'x_label': getattr(result.chart, 'x_label', ''),
                        'y_label': getattr(result.chart, 'y_label', ''),
                        'elements': []
                    }
                    # Extraire les données du graphique
                    if hasattr(result.chart, 'elements') and result.chart.elements:
                        for element in result.chart.elements:
                            chart_data['elements'].append({
                                'label': str(getattr(element, 'label', '')),
                                'value': float(getattr(element, 'value', 0)) if hasattr(element, 'value') else 0,
                                'group': str(getattr(element, 'group', '')) if hasattr(element, 'group') else ''
                            })
                    results['results'].append(chart_data)
                # Méthode 4: Texte ou données brutes
                elif hasattr(result, '__str__'):
                    text_content = str(result)
                    if text_content and text_content != 'None':
                        results['results'].append({
                            'type': 'text',
                            'content': text_content
                        })
        
        return results

def generate_analysis_code(analysis_request: str) -> str:
    """
    Génère du code d'analyse basé sur la demande
    (Ceci pourrait être fait par CrewAI sur le VPS)
    """
    return f'''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Charger les données
df = pd.read_csv('dataset.csv')
print(f"📊 Dataset: {{df.shape[0]}} lignes, {{df.shape[1]}} colonnes")
print(f"📋 Colonnes: {{df.columns.tolist()}}")

# Analyse demandée: {analysis_request}

# 1. Statistiques descriptives
print("\\n📈 STATISTIQUES DESCRIPTIVES")
print("="*50)
print(df.describe())

# 2. Informations sur les données
print("\\n📋 INFORMATIONS DATASET")  
print("="*50)
missing = df.isnull().sum()
if missing.sum() > 0:
    print("Valeurs manquantes:")
    for col, count in missing[missing > 0].items():
        print(f"  • {{col}}: {{count}} ({{count/len(df)*100:.1f}}%)")
else:
    print("✅ Aucune valeur manquante")

# 3. Visualisations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Dashboard d\\'analyse', fontsize=14, fontweight='bold')

# Distribution première colonne numérique
numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
if numeric_cols:
    df[numeric_cols[0]].hist(ax=axes[0,0], bins=20, edgecolor='black')
    axes[0,0].set_title(f'Distribution {{numeric_cols[0]}}')

# Top catégories
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
if categorical_cols:
    df[categorical_cols[0]].value_counts()[:10].plot(kind='bar', ax=axes[0,1])
    axes[0,1].set_title(f'Top 10 {{categorical_cols[0]}}')

# Corrélations
if len(numeric_cols) >= 2:
    corr_matrix = df[numeric_cols].corr()
    sns.heatmap(corr_matrix, annot=True, ax=axes[1,0], cmap='coolwarm', fmt='.2f')
    axes[1,0].set_title('Matrice de corrélation')

# Résumé
summary_text = f"Résumé:\\n"
summary_text += f"• Lignes: {{len(df)}}\\n"
summary_text += f"• Colonnes: {{len(df.columns)}}\\n"
summary_text += f"• Types: {{df.dtypes.value_counts().to_dict()}}"
axes[1,1].text(0.1, 0.5, summary_text, fontsize=10, va='center')
axes[1,1].axis('off')

plt.tight_layout()
plt.show()  # E2B capture automatiquement les graphiques matplotlib

# 4. Insights automatiques
print("\\n💡 INSIGHTS")
print("="*50)

# Corrélations fortes
if len(numeric_cols) >= 2:
    corr_matrix = df[numeric_cols].corr()
    strong_corr = []
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            corr_val = abs(corr_matrix.iloc[i, j])
            if corr_val > 0.7:
                strong_corr.append((numeric_cols[i], numeric_cols[j], corr_val))
    
    if strong_corr:
        print("Corrélations fortes détectées:")
        for c1, c2, val in strong_corr:
            print(f"  • {{c1}} ↔ {{c2}}: {{val:.2f}}")

# Outliers
for col in numeric_cols[:3]:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
    if outliers > 0:
        print(f"  • {{outliers}} outliers dans {{col}}")

print("\\n✅ ANALYSE TERMINÉE")
'''