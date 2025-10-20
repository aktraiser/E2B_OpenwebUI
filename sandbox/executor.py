"""
Exécuteur pour le sandbox E2B - Lance CrewAI dans l'environnement isolé
"""

from e2b_code_interpreter import Sandbox
import tempfile
import os

def execute_crew_in_sandbox(csv_data: str, analysis_request: str) -> dict:
    """
    Exécute l'analyse CrewAI complète dans le sandbox E2B
    
    Args:
        csv_data: Contenu CSV en string ou chemin vers fichier
        analysis_request: Demande d'analyse de l'utilisateur
        
    Returns:
        Résultats de l'analyse avec graphiques et insights
    """
    
    # Code CrewAI à exécuter dans le sandbox
    crew_code = f'''
# Installation des dépendances avec versions compatibles
import subprocess
import sys
print("📦 Installation de CrewAI et E2B...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pydantic==2.8.2", "crewai==0.70.1", "pandas", "matplotlib", "seaborn"])

# Import des bibliothèques
from crewai.tools import tool
from crewai import Agent, Task, Crew, LLM
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Charger les données
print("📊 Chargement des données...")
df = pd.read_csv('dataset.csv')
print(f"Dataset: {{df.shape[0]}} lignes, {{df.shape[1]}} colonnes")

# Définir l'outil principal d'analyse
@tool("Python Analyzer")
def analyze_data(query: str) -> str:
    """Execute data analysis code"""
    try:
        # Analyse basée sur la requête
        if "describe" in query.lower():
            return str(df.describe())
        elif "correlation" in query.lower():
            return str(df.corr())
        elif "missing" in query.lower():
            return str(df.isnull().sum())
        else:
            return f"Analysis completed for: {{query}}"
    except Exception as e:
        return f"Error: {{str(e)}}"

# Créer l'agent principal
analyst = Agent(
    role='Senior Data Analyst',
    goal='Perform comprehensive analysis of the dataset',
    backstory="""You are an expert data analyst with 10+ years of experience.
    You excel at finding patterns, creating visualizations, and providing insights.""",
    tools=[analyze_data],
    llm=LLM(model="gpt-4o")
)

# Créer la tâche d'analyse
analysis_task = Task(
    description="""
    Analyze the loaded dataset and provide:
    1. Data quality assessment
    2. Key statistics and patterns
    3. Relevant visualizations
    4. Business insights
    
    User request: {analysis_request}
    """,
    agent=analyst,
    expected_output="Complete analysis with visualizations and recommendations"
)

# Créer et exécuter la crew
print("🚀 Lancement de l'analyse CrewAI...")
crew = Crew(
    agents=[analyst],
    tasks=[analysis_task],
    verbose=True
)

# Exécuter l'analyse
result = crew.kickoff()

# Créer des visualisations
print("📈 Génération des visualisations...")
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Graph 1: Distribution de la première colonne numérique
numeric_cols = df.select_dtypes(include=['number']).columns
if len(numeric_cols) > 0:
    df[numeric_cols[0]].hist(ax=axes[0,0], bins=20)
    axes[0,0].set_title(f'Distribution de {{numeric_cols[0]}}')

# Graph 2: Corrélation
if len(numeric_cols) > 1:
    corr_matrix = df[numeric_cols].corr()
    sns.heatmap(corr_matrix, annot=True, ax=axes[0,1], cmap='coolwarm')
    axes[0,1].set_title('Matrice de corrélation')

# Graph 3: Top categories
categorical_cols = df.select_dtypes(include=['object']).columns
if len(categorical_cols) > 0:
    df[categorical_cols[0]].value_counts()[:10].plot(kind='bar', ax=axes[1,0])
    axes[1,0].set_title(f'Top 10 {{categorical_cols[0]}}')

# Graph 4: Résumé
summary = f"Analyse CrewAI\\n"
summary += f"Lignes: {{len(df)}}\\n"
summary += f"Colonnes: {{len(df.columns)}}\\n"
summary += f"Types: {{df.dtypes.value_counts().to_dict()}}"
axes[1,1].text(0.1, 0.5, summary, fontsize=12)
axes[1,1].axis('off')

plt.tight_layout()
plt.savefig('analysis_dashboard.png')
plt.show()

print("✅ Analyse CrewAI terminée!")
print(f"\\nRésultat final:\\n{{result}}")
'''
    
    # Exécuter dans le sandbox E2B
    with Sandbox.create() as sandbox:
        # Écrire le CSV dans le sandbox
        if os.path.exists(csv_data):
            # C'est un fichier
            with open(csv_data, 'r') as f:
                csv_content = f.read()
        else:
            # C'est du contenu direct
            csv_content = csv_data
            
        sandbox.files.write('dataset.csv', csv_content)
        
        # Exécuter le code CrewAI
        print("🤖 Exécution de CrewAI dans le sandbox E2B...")
        execution = sandbox.run_code(crew_code)
        
        # Collecter les résultats
        results = {
            'success': not execution.error,
            'output': execution.text if execution.text else "",
            'logs': execution.logs,
            'results': []
        }
        
        # Ajouter les erreurs si présentes
        if execution.error:
            results['error'] = {
                'name': execution.error.name,
                'value': execution.error.value,
                'traceback': execution.error.traceback
            }
        
        # Traiter les résultats (graphiques, données, etc.)
        for result in execution.results:
            if result.chart:
                results['results'].append({
                    'type': 'chart',
                    'data': result.chart
                })
            elif result.data:
                results['results'].append({
                    'type': 'data',
                    'content': result.data
                })
        
        return results