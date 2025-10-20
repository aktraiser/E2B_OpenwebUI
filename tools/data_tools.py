"""
Outils CrewAI pour l'analyse de données avec E2B
Ces outils tournent sur le VPS et utilisent E2B pour l'exécution
"""

from crewai.tools import tool
from e2b_code_interpreter import Sandbox

@tool("Python Data Analyzer")
def execute_python_analysis(code: str) -> str:
    """
    Execute Python code for data analysis in E2B sandbox
    L'outil tourne sur le VPS, le code s'exécute dans E2B
    """
    with Sandbox.create() as sandbox:
        # Si on a un dataset en contexte, l'uploader
        if hasattr(execute_python_analysis, 'current_dataset'):
            sandbox.files.write('dataset.csv', execute_python_analysis.current_dataset)
        
        execution = sandbox.run_code(code)
        
        if execution.error:
            return f"Error: {execution.error.name}: {execution.error.value}"
        
        return execution.text or "Code executed successfully"

@tool("CSV Loader")
def load_csv_data(csv_path: str) -> str:
    """
    Load and describe a CSV file
    """
    code = f"""
import pandas as pd
df = pd.read_csv('{csv_path}')
print(f"Dataset shape: {{df.shape}}")
print(f"Columns: {{df.columns.tolist()}}")
print("\\nFirst 5 rows:")
print(df.head())
print("\\nData types:")
print(df.dtypes)
print("\\nBasic statistics:")
print(df.describe())
"""
    return execute_python_analysis(code)

@tool("Data Profiler")
def profile_data(csv_path: str) -> str:
    """
    Generate comprehensive data profile
    """
    code = f"""
import pandas as pd
df = pd.read_csv('{csv_path}')

# Missing values
print("Missing values:")
print(df.isnull().sum())

# Unique values
print("\\nUnique values per column:")
for col in df.columns:
    print(f"{{col}}: {{df[col].nunique()}}")

# Memory usage
print("\\nMemory usage:")
print(df.memory_usage(deep=True))
"""
    return execute_python_analysis(code)