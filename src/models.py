from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enum pour les niveaux de priorité
class PriorityLevel(str, Enum):
    P1 = "P1"  # Prio la plus haute (ex: examen)
    P2 = "P2"  # Prio moyenne (ex: devoir)
    P3 = "P3"  # Prio la plus basse (ex: info)

# Enum pour les rôles utilisateurs
class Role(str, Enum):
    ENSEIGNANT = "enseignant"
    ELEVE = "eleve"

# Modèle de données pour un événement
class Event(BaseModel):
    title: str
    date: datetime 
    priority: PriorityLevel = PriorityLevel.P2  # par défaut prio moyenne

# Modèle utilisateurs (enseignants ou élèves)
class User(BaseModel):
    username: str
    hashed_password: str
    full_name: str | None = None
    email: str | None = None
    disabled: bool | None = None
    role: Role  

# Modèle utilisateur pour le stock en base de données
class UserInDB(User):
    private_agenda: List[Event] = []  # chaque user a un agenda privé