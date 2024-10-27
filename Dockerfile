# Utiliser une image Python officielle
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /src

# Copier les fichiers de dépendances
COPY pyproject.toml .

# Installer les dépendances
RUN pip install --no-cache-dir .

# Copier le reste du code
COPY . .

# Expose
EXPOSE 8000  
EXPOSE 9090  
EXPOSE 5672  

# Commande pour démarrer l'application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]