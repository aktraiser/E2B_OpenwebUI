"""
Outils de visualisation pour CrewAI avec E2B
"""

from crewai.tools import tool
from e2b_code_interpreter import Sandbox

@tool("Chart Generator")
def create_e2b_chart(chart_type: str, data_config: dict) -> str:
    """
    Create charts using E2B's visualization capabilities
    """
    code = f"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
chart_type = '{chart_type}'
config = {data_config}

df = pd.read_csv('dataset.csv')

plt.figure(figsize=(10, 6))

if chart_type == 'bar':
    df.groupby(config['x'])[config['y']].sum().plot(kind='bar')
elif chart_type == 'scatter':
    plt.scatter(df[config['x']], df[config['y']])
elif chart_type == 'heatmap':
    correlation_matrix = df.select_dtypes(include=['number']).corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
elif chart_type == 'line':
    df.plot(x=config['x'], y=config['y'], kind='line')
else:
    df.plot()

plt.title(config.get('title', f'{{chart_type.title()}} Chart'))
plt.xlabel(config.get('xlabel', ''))
plt.ylabel(config.get('ylabel', ''))
plt.tight_layout()
plt.show()

print(f"Chart '{{chart_type}}' created successfully")
"""
    
    with Sandbox.create() as sandbox:
        execution = sandbox.run_code(code)
        return execution.text

@tool("Dashboard Creator")
def create_dashboard(csv_path: str, metrics: list) -> str:
    """
    Create a comprehensive dashboard with multiple visualizations
    """
    code = f"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('{csv_path}')
metrics = {metrics}

fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Data Analysis Dashboard', fontsize=16)

# Subplot 1: Distribution of first numeric column
numeric_cols = df.select_dtypes(include=['number']).columns
if len(numeric_cols) > 0:
    axes[0, 0].hist(df[numeric_cols[0]], bins=20, edgecolor='black')
    axes[0, 0].set_title(f'Distribution of {{numeric_cols[0]}}')

# Subplot 2: Bar chart of categories
categorical_cols = df.select_dtypes(include=['object']).columns
if len(categorical_cols) > 0:
    df[categorical_cols[0]].value_counts().plot(kind='bar', ax=axes[0, 1])
    axes[0, 1].set_title(f'Count by {{categorical_cols[0]}}')

# Subplot 3: Correlation heatmap (simplified)
if len(numeric_cols) > 1:
    corr = df[numeric_cols].corr()
    im = axes[1, 0].imshow(corr, cmap='coolwarm', aspect='auto')
    axes[1, 0].set_title('Correlation Matrix')
    plt.colorbar(im, ax=axes[1, 0])

# Subplot 4: Summary statistics
summary_text = f"Dataset Info:\\n"
summary_text += f"Rows: {{len(df)}}\\n"
summary_text += f"Columns: {{len(df.columns)}}\\n"
if len(numeric_cols) > 0:
    summary_text += f"\\nKey Metrics:\\n"
    for col in numeric_cols[:3]:
        summary_text += f"{{col}}:\\n  Mean: {{df[col].mean():.2f}}\\n  Std: {{df[col].std():.2f}}\\n"

axes[1, 1].text(0.1, 0.5, summary_text, fontsize=10, verticalalignment='center')
axes[1, 1].axis('off')

plt.tight_layout()
plt.show()

print("Dashboard created successfully")
"""
    
    with Sandbox.create() as sandbox:
        execution = sandbox.run_code(code)
        return execution.text