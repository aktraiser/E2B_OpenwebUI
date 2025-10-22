# 🚀 Guide CrewAI : Comprendre les Teams d'IA

## 📖 Introduction

**CrewAI** est un framework Python qui permet de créer des **équipes d'agents IA** qui collaborent pour résoudre des tâches complexes. Chaque agent a un rôle spécifique, des outils, et travaille ensemble vers un objectif commun.

## 🏗️ Architecture CrewAI

```
┌─────────────────────────────────────────────────────────┐
│                      CREW                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   AGENT 1   │  │   AGENT 2   │  │   AGENT 3   │     │
│  │    Role     │  │    Role     │  │    Role     │     │
│  │    Goal     │  │    Goal     │  │    Goal     │     │
│  │   Tools     │  │   Tools     │  │   Tools     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│         │                │                │           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   TASK 1    │  │   TASK 2    │  │   TASK 3    │     │
│  │Description  │  │Description  │  │Description  │     │
│  │Expected Out │  │Expected Out │  │Expected Out │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## 🧩 Composants Principaux

### 1. **Agent** 🤖
Un agent IA avec une personnalité et des capacités spécifiques.

```python
from crewai import Agent, LLM

agent = Agent(
    role='Data Analyst',                    # Son rôle
    goal='Analyze data and find insights',  # Son objectif
    backstory='Expert in data science...',  # Sa personnalité
    tools=[python_tool, csv_tool],         # Ses outils
    llm=LLM(model="gpt-4o"),               # Son cerveau IA
    verbose=True                           # Affiche ses pensées
)
```

### 2. **Task** 📋
Une tâche spécifique à accomplir.

```python
from crewai import Task

task = Task(
    description="Analyze the CSV file and calculate averages",
    agent=data_analyst,                    # Qui fait la tâche
    expected_output="Statistical summary with averages"
)
```

### 3. **Tool** 🛠️
Un outil que les agents peuvent utiliser.

```python
from crewai.tools import tool

@tool("Python Executor")
def execute_python(code: str) -> str:
    """Execute Python code and return results"""
    # Code d'exécution
    return result
```

### 4. **Crew** 👥
L'équipe qui coordonne agents et tâches.

```python
from crewai import Crew

crew = Crew(
    agents=[data_analyst, researcher],     # Les agents
    tasks=[analyze_task, report_task],     # Les tâches
    verbose=True                           # Voir le travail d'équipe
)

result = crew.kickoff()  # 🚀 Lancer l'équipe !
```

## 🔄 Notre Implémentation E2B

### Architecture de notre système

```python
# 1. Définir l'outil E2B
@tool("Python Interpreter")
def execute_python(code: str) -> str:
    """Execute Python code in E2B sandbox"""
    with Sandbox.create() as sandbox:
        execution = sandbox.run_code(code)
        return execution.text

# 2. Créer l'agent
python_executor = Agent(
    role='Python Executor and Researcher',
    goal='Execute Python code and solve complex tasks',
    backstory='Expert Python programmer and researcher',
    tools=[execute_python],                # ← Notre outil E2B
    llm=LLM(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
)

# 3. Définir la tâche
execute_task = Task(
    description=task_description,          # ← Vient d'OpenWebUI
    agent=python_executor,
    expected_output="Complete solution with execution results"
)

# 4. Créer l'équipe
crew = Crew(
    agents=[python_executor],
    tasks=[execute_task],
    verbose=True
)

# 5. Exécuter !
result = crew.kickoff()  # 🚀
```

## 🌟 Concepts Avancés

### **Process Flow** 🔄

1. **Sequential** (défaut) : Tâches une par une
2. **Hierarchical** : Agent manager + équipe
3. **Consensus** : Décision collective

```python
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    process=Process.sequential  # ou hierarchical, consensus
)
```

### **Memory & Context** 🧠

```python
crew = Crew(
    agents=[agent],
    tasks=[task],
    memory=True,           # Se souvient des interactions
    cache=True,            # Cache les résultats
    max_execution_time=300 # Timeout 5 minutes
)
```

### **Delegation** 🤝

```python
researcher = Agent(
    role='Researcher',
    allow_delegation=True,  # Peut déléguer à d'autres agents
    tools=[search_tool]
)
```

## 💡 Exemples Pratiques

### **Exemple 1 : Analyse de données simple**

```python
# Agent spécialisé
data_analyst = Agent(
    role='Data Analyst',
    goal='Analyze CSV data and provide insights',
    backstory='Statistical expert with Python skills',
    tools=[execute_python],
    llm=LLM(model="gpt-4o")
)

# Tâche d'analyse
analyze_task = Task(
    description="Load CSV data, calculate statistics, and create summary",
    agent=data_analyst,
    expected_output="Statistical summary with key insights"
)

# Lancer l'analyse
crew = Crew(agents=[data_analyst], tasks=[analyze_task])
result = crew.kickoff()
```

### **Exemple 2 : Équipe multi-agents**

```python
# Agent 1 : Collecteur de données
data_collector = Agent(
    role='Data Collector',
    goal='Gather and clean data',
    tools=[file_reader, data_cleaner]
)

# Agent 2 : Analyste
data_analyst = Agent(
    role='Data Analyst', 
    goal='Perform statistical analysis',
    tools=[execute_python, visualization_tool]
)

# Agent 3 : Rapporteur
report_writer = Agent(
    role='Report Writer',
    goal='Create comprehensive reports',
    tools=[markdown_generator]
)

# Tâches séquentielles
task1 = Task(description="Collect and clean data", agent=data_collector)
task2 = Task(description="Analyze cleaned data", agent=data_analyst)
task3 = Task(description="Write final report", agent=report_writer)

# Équipe collaborative
crew = Crew(
    agents=[data_collector, data_analyst, report_writer],
    tasks=[task1, task2, task3],
    process=Process.sequential
)
```

## 🔧 Configuration dans notre système

### **Variables d'environnement**
```bash
OPENAI_API_KEY=sk-...          # Pour CrewAI LLM
E2B_API_KEY=e2b_...           # Pour les sandboxes E2B
```

### **Flow d'exécution**
```
OpenWebUI → FastAPI → CrewAI → E2B Sandbox → Résultat
    ↑                                            ↓
    └─────────── Retour du résultat ←────────────┘
```

## 🎯 Avantages de CrewAI

### ✅ **Pour notre cas d'usage**
- **Simplicité** : Un agent = une responsabilité
- **Flexibilité** : Facile d'ajouter de nouveaux agents/outils
- **Sécurité** : Exécution isolée dans E2B
- **Traçabilité** : Logs détaillés avec `verbose=True`

### ✅ **Cas d'usage étendus**
- **Analyse de données** : CSV, JSON, bases de données
- **Recherche** : Web scraping, APIs, documents
- **Génération de code** : Python, SQL, scripts
- **Rapports** : Markdown, HTML, PDF
- **Automatisation** : Workflows complexes

## 🚀 Extensions possibles

### **Ajouter de nouveaux outils**
```python
@tool("Web Searcher")
def search_web(query: str) -> str:
    """Search the web for information"""
    # Implementation avec requests, BeautifulSoup, etc.
    return results

@tool("Database Query")
def query_database(sql: str) -> str:
    """Execute SQL queries"""
    # Implementation avec SQLAlchemy, pandas, etc.
    return results
```

### **Agents spécialisés**
```python
# Agent pour l'IA/ML
ml_engineer = Agent(
    role='ML Engineer',
    goal='Build and train machine learning models',
    tools=[execute_python, model_trainer, data_visualizer]
)

# Agent pour la cybersécurité
security_analyst = Agent(
    role='Security Analyst', 
    goal='Analyze logs and detect threats',
    tools=[log_analyzer, threat_detector]
)
```

## 📚 Ressources

- **Documentation officielle** : https://docs.crewai.com/
- **Exemples** : https://github.com/joaomdmoura/crewAI-examples
- **Community** : https://discord.gg/X4JWnZnxPb

## 🎉 Conclusion

CrewAI transforme des tâches complexes en collaboration d'agents spécialisés. Dans notre implémentation, nous avons créé un agent Python qui utilise E2B pour exécuter du code en toute sécurité, le tout intégré dans OpenWebUI via une API REST.

**Le résultat** : Un système puissant, extensible et sécurisé pour l'analyse de données et l'exécution de code ! 🚀