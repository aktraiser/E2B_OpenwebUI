FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY mcp_server.py .
COPY .env* ./

# Créer un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exposer le port
EXPOSE 8091

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV MCPO_PORT=8091

# Commande pour démarrer MCPO avec le serveur MCP
CMD ["mcpo", "--host", "0.0.0.0", "--port", "8091", "--api-key", "csv-analyzer-api-key", "--", "python", "mcp_server.py"]