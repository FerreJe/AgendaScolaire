# ---- Import des bibliothèques nécessaires ----
from typing import Annotated, List, Optional
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Import de nos modules personnalisés
from src.models import UserInDB, Event, PriorityLevel
from src.publisher import publish_class_event, publish_private_event, publish_private_event_update
from src.fake_db import fake_users_db, fake_classes_db  
from src.notification_manager import NotificationManager
from src.metrics import api_requests, notifications_sent, events_total

# ---- Configuration de FastAPI et du gestionnaire de notifications ----
app = FastAPI()
notification_manager = NotificationManager()

# ---- Configuration OAuth2 pour l'authentification ----
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def fake_hash_password(password: str):
    """Simulation du hachage de mot de passe"""
    return "fakehashed" + password

def get_user(db, username: str):
    """Récupère un utilisateur depuis la base de données"""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def fake_decode_token(token):
    """Simule le décodage du token"""
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Vérifie et retourne l'utilisateur actuel basé sur le token"""
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
):
    """Vérifie si l'utilisateur est actif"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Endpoint pour la connexion"""
    api_requests.labels(endpoint='/token').inc()
    
    print("Tentative de connexion avec l'utilisateur:", form_data.username)
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        print("Utilisateur introuvable dans la base de données fictive.")
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    print("Mot de passe haché:", hashed_password)
    if not hashed_password == user.hashed_password:
        print("Le mot de passe haché ne correspond pas.")
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    print("Connexion réussie pour l'utilisateur:", form_data.username)
    return {"access_token": user.username, "token_type": "bearer"}

# ----- CREATE ----- 

@app.post("/users/me/agenda")
async def add_private_event(
    event: Event, 
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    """Ajoute un événement privé dans l'agenda de l'utilisateur"""
    # Incrémentation des métriques
    api_requests.labels(endpoint='/users/me/agenda').inc()
    events_total.labels(type='private').inc()
    
    # Conversion de la date
    if type(event.date) == str:
        event.date = datetime.strptime(event.date, "%d/%m/%Y")
    
    # Ajoute l'événement à l'agenda
    current_user.private_agenda.append(event)
    fake_users_db[current_user.username]["private_agenda"] = current_user.private_agenda
    
    # Publication et notification
    publish_private_event(event)
    notification_manager.send_notification(event)
    notifications_sent.labels(priority=event.priority.value).inc()
    
    return {
        "message": "Événement privé ajouté",
        "agenda": current_user.private_agenda
    }

@app.post("/classe/{class_name}")
async def create_shared_event(
    class_name: str, 
    event: Event, 
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    """Crée un événement partagé pour une classe"""
    # Incrémentation des métriques
    api_requests.labels(endpoint=f'/classe/{class_name}').inc()
    events_total.labels(type='shared').inc()
    
    # Vérifications
    if current_user.role != "enseignant":
        raise HTTPException(status_code=403, detail="Seuls les enseignants peuvent créer des événements partagés.")
    
    class_info = fake_classes_db.get(class_name)
    if class_info is None or class_info["teacher"] != current_user.username:
        raise HTTPException(status_code=403, detail=f"Vous n'êtes pas l'enseignant de la classe {class_name}.")
    
    if "events" not in class_info:
        class_info["events"] = []

    # Ajoute aux agendas des élèves
    for student_username in class_info["students"]:
        student = get_user(fake_users_db, student_username)
        if student:
            student.private_agenda.append(event)
            fake_users_db[student.username]["private_agenda"] = student.private_agenda

    # Ajoute à la classe
    class_info["events"].append(event)
    fake_classes_db[class_name] = class_info

    # Notifications
    message = f"{current_user.full_name} a ajouté une affectation | Échéance: {event.date.strftime('%d/%m/%Y')} | Classe: {class_name}"
    publish_class_event(message, class_name)
    notification_manager.send_notification(event, class_name=class_name)
    notifications_sent.labels(priority=event.priority.value).inc()

    return {
        "message": f"Événement partagé créé pour la classe {class_name}"
    }
    
    # ----- READ ----- 

@app.get("/users/me/agenda")
async def read_private_events(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    """Récupère tous les événements privés de l'utilisateur"""
    api_requests.labels(endpoint='/users/me/agenda').inc()
        
    return current_user.private_agenda

@app.get("/classe/{class_name}/events")
async def read_shared_events(
    class_name: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
):
    """Récupère les événements d'une classe"""
    api_requests.labels(endpoint=f'/classe/{class_name}/events').inc()
    
    class_info = fake_classes_db.get(class_name)
    if class_info is None:
        raise HTTPException(status_code=404, detail="Classe non trouvée")

    if current_user.role == "eleve" and current_user.username not in class_info["students"]:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas abonné à cette classe")

    return class_info.get("events", [])

# ----- FILTER -----

@app.get("/users/me/agenda/filter")
async def filter_private_events(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    date: Optional[str] = None,
    priority: Optional[PriorityLevel] = None,
):
    """Filtre les événements privés par date et/ou priorité"""
    api_requests.labels(endpoint='/users/me/agenda/filter').inc()
    
    filtered_events = current_user.private_agenda

    # Filtre par date
    if date:
        target_date = datetime.strptime(date, "%d/%m/%Y")
        filtered_events = [
            event for event in filtered_events 
            if event.date.date() == target_date.date()
        ]

    # Filtre par priorité
    if priority:
        filtered_events = [
            event for event in filtered_events 
            if event.priority == priority
        ]

    return filtered_events

@app.get("/classe/{class_name}/events/filter")
async def filter_shared_events(
    class_name: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    date: Optional[str] = None,
    priority: Optional[PriorityLevel] = None,
):
    """Filtre les événements d'une classe par date et/ou priorité"""
    api_requests.labels(endpoint=f'/classe/{class_name}/events/filter').inc()
    
    class_info = fake_classes_db.get(class_name)
    if class_info is None:
        raise HTTPException(status_code=404, detail="Classe non trouvée")

    if current_user.role == "eleve" and current_user.username not in class_info["students"]:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas abonné à cette classe")

    filtered_events = class_info.get("events", [])

    # Filtre par date
    if date:
        target_date = datetime.strptime(date, "%d/%m/%Y")
        filtered_events = [
            event for event in filtered_events 
            if event.date.date() == target_date.date()
        ]

    # Filtre par priorité
    if priority:
        filtered_events = [
            event for event in filtered_events 
            if event.priority == priority
        ]

    return filtered_events

# ----- UPDATE -----

@app.put("/users/me/agenda/by_title/{event_title}")
async def update_private_event(
    event_title: str, 
    updated_event: Event, 
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    """Mise à jour d'un événement privé par titre"""
    api_requests.labels(endpoint='/users/me/agenda/update').inc()
    
    # Recherche de l'événement
    found_event = None
    for event in current_user.private_agenda:
        if event.title == event_title:
            found_event = event
            break

    if found_event is None:
        raise HTTPException(status_code=404, detail="Événement avec ce titre non trouvé")

    # Mise à jour de l'événement
    found_event.title = updated_event.title
    if type(updated_event.date) == str:
        found_event.date = datetime.strptime(updated_event.date, "%d/%m/%Y")
    else:
        found_event.date = updated_event.date
    found_event.priority = updated_event.priority

    # Mise à jour base de données et notification
    fake_users_db[current_user.username]["private_agenda"] = current_user.private_agenda
    publish_private_event_update(found_event)
    notification_manager.send_notification(found_event, user_name=current_user.full_name)
    notifications_sent.labels(priority=found_event.priority.value).inc()

    return {
        "message": "Événement privé mis à jour",
        "event": found_event
    }

@app.put("/classe/{class_name}/events/by_title/{event_title}")
async def update_shared_event(
    class_name: str, 
    event_title: str, 
    updated_event: Event, 
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    """Mise à jour d'un événement partagé"""
    api_requests.labels(endpoint=f'/classe/{class_name}/events/update').inc()
    
    if current_user.role != "enseignant":
        raise HTTPException(status_code=403, detail="Seuls les enseignants peuvent modifier des événements partagés")

    class_info = fake_classes_db.get(class_name)
    if class_info is None:
        raise HTTPException(status_code=404, detail="Classe non trouvée")

    # Recherche de l'événement
    found_event = None
    for event in class_info.get("events", []):
        if event.title == event_title:
            found_event = event
            break

    if found_event is None:
        raise HTTPException(status_code=404, detail="Événement avec ce titre non trouvé")

    # Mise à jour de l'événement
    found_event.title = updated_event.title
    if type(updated_event.date) == str:
        found_event.date = datetime.strptime(updated_event.date, "%d/%m/%Y")
    else:
        found_event.date = updated_event.date
    found_event.priority = updated_event.priority

    # Mise à jour des agendas des élèves
    for student_username in class_info["students"]:
        student = get_user(fake_users_db, student_username)
        if student:
            for private_event in student.private_agenda:
                if private_event.title == event_title:
                    private_event.title = updated_event.title
                    private_event.date = found_event.date
                    private_event.priority = updated_event.priority
            fake_users_db[student.username]["private_agenda"] = student.private_agenda

    # Notification de la mise à jour
    message = f"{current_user.full_name} a mis à jour '{event_title}' | Nouvelle échéance: {found_event.date.strftime('%d/%m/%Y')}"
    publish_class_event(message, class_name)
    notification_manager.send_notification(found_event, class_name=class_name)
    notifications_sent.labels(priority=found_event.priority.value).inc()

    return {
        "message": f"Événement partagé modifié pour la classe {class_name}",
        "event": found_event
    }
    
# ----- DELETE -----

@app.delete("/users/me/agenda/by_title/{event_title}")
async def delete_private_event(
    event_title: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    """Supprime un événement privé par titre"""
    api_requests.labels(endpoint='/users/me/agenda/delete').inc()
    
    # Recherche et suppression de l'événement
    for i, event in enumerate(current_user.private_agenda):
        if event.title == event_title:
            deleted_event = current_user.private_agenda.pop(i)
            
            # Mise à jour de la base de données
            fake_users_db[current_user.username]["private_agenda"] = current_user.private_agenda
            
            # Notification de suppression
            notification_manager.send_notification(deleted_event, user_name=current_user.full_name)
            notifications_sent.labels(priority=deleted_event.priority.value).inc()
            
            return {
                "message": "Événement privé supprimé",
                "deleted_event": deleted_event
            }
    
    raise HTTPException(status_code=404, detail="Événement avec ce titre non trouvé")

@app.delete("/classe/{class_name}/events/by_title/{event_title}")
async def delete_shared_event(
    class_name: str,
    event_title: str,
    current_user: Annotated[UserInDB, Depends(get_current_active_user)]
):
    """Supprime un événement partagé d'une classe"""
    api_requests.labels(endpoint=f'/classe/{class_name}/events/delete').inc()
    
    if current_user.role != "enseignant":
        raise HTTPException(status_code=403, detail="Seuls les enseignants peuvent supprimer des événements partagés")
    
    class_info = fake_classes_db.get(class_name)
    if class_info is None:
        raise HTTPException(status_code=404, detail="Classe non trouvée")
    
    # Recherche et suppression de l'événement
    deleted_event = None
    events = class_info.get("events", [])
    for i, event in enumerate(events):
        if event.title == event_title:
            deleted_event = events.pop(i)
            break
    
    if deleted_event is None:
        raise HTTPException(status_code=404, detail="Événement avec ce titre non trouvé")
    
    # Suppression dans les agendas des élèves
    for student_username in class_info["students"]:
        student = get_user(fake_users_db, student_username)
        if student:
            student.private_agenda = [
                event for event in student.private_agenda 
                if event.title != event_title
            ]
            fake_users_db[student.username]["private_agenda"] = student.private_agenda
    
    # Notification de suppression
    message = f"L'événement '{event_title}' a été supprimé de la classe {class_name}"
    publish_class_event(message, class_name)
    notification_manager.send_notification(deleted_event, class_name=class_name)
    notifications_sent.labels(priority=deleted_event.priority.value).inc()
    
    return {
        "message": f"Événement supprimé de la classe {class_name}",
        "deleted_event": deleted_event
    }

# ----- Nettoyage à l'arrêt de l'application -----
@app.on_event("shutdown")
async def shutdown_event():
    """Ferme proprement les connexions à l'arrêt de l'application"""
    notification_manager.close()