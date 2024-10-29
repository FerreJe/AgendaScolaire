# Image Python 
FROM python:latest

# Définir le répertoire de travail
WORKDIR /src

# Installer setuptools et wheel pour construire le projet
RUN pip install --no-cache-dir setuptools wheel

# Copier tout le code du projet pour inclure pyproject.toml, README.md, et src/
COPY . .

# Créer un fichier README.md vide si nécessaire (pour éviter l'erreur)
RUN touch README.md

# Installer les dépendances du projet
RUN pip install --no-cache-dir .

# Exposer les ports nécessaires pour l’API, Prometheus et RabbitMQ
EXPOSE 8000   
EXPOSE 9090   
EXPOSE 15672  
# Commande pour démarrer l'application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
