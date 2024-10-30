# Agenda Scolaire avec Notifications

Un système d'agenda scolaire permettant aux enseignants de créer et gérer des événements (examens, devoirs) et aux élèves de recevoir des notifications selon le niveau de priorité.

## Table des matières
1. [Installation](#installation)
2. [Démarrage du système](#démarrage-du-système)
3. [Utilisation de l'application](#utilisation-de-lapplication)
4. [Monitoring](#monitoring)

## Installation

### Pré-requis
- Docker Desktop ([Télécharger ici](https://www.docker.com/products/docker-desktop/))


### Mise en place
1. Téléchargez ou clonez ce projet sur votre ordinateur
2. Ouvrez un terminal et naviguez vers le dossier du projet
3. Démarrez le système


## Démarrage du système

Vous aurez besoin d'un terminal pour exécuter les composants du système.

### Terminal 1 - Services Docker
```bash
docker compose up --build
```

Une fois tout démarré, vérifiez que :
- Le terminal avec subscriber.py affiche "Connexion réussie à RabbitMQ"
- Vous voyez les logs de FastAPI indiquant que l'application est démarrée
- L'interface Swagger est accessible

## Utilisation de l'application

### 1. Accès aux services
- API et Interface Swagger : http://localhost:8002/docs
- RabbitMQ : http://localhost:15672 (guest/guest)
- Grafana : http://localhost:3000 (admin/admin)
- Prometheus : http://localhost:9090/targets
- Metrics : http://localhost:8003/metrics

### 2. Connexion à l'application

L'application propose deux types d'utilisateurs :

**Exemple Enseignant :**
- Identifiant : JerMac
- Mot de passe : fakehashedpwd4m321prof

**Exemple Élève :**
- Identifiant : JessFerr
- Mot de passe : fakehashedpwd4m321student

**Gestion des événements**

L'application utilise trois niveaux de priorité pour les événements :
- P1 : Examens (notification 2 jours avant)
- P2 : Devoirs (notification 1 jour avant)
- P3 : Informations (notification le jour même)

### 3. Utilisation de l'API via l'interface Swagger

### Accéder à Swagger :
Pour se connecter via l'interface Swagger :

1. Ouvrez [http://localhost:8002/docs](http://localhost:8002/docs) dans votre navigateur.
2. Utilisez le token en cliquant sur le bouton "Authorize" en haut de la page
2. Saisir le username et password
3. Cliquez Authorise
4. Cliquez sur l'endpoint souhaité pour l’ouvrir.
5. Utilisez **Try out** pour entrer les données et tester les requêtes directement depuis l'interface.

---

### Pour les enseignants :

- **Créer un événement de classe** : `/classe/{class_name}` [POST]
  - Accédez à l’endpoint `/classe/{class_name}` dans Swagger.
  - Cliquez sur **Try out**.
  - Dans **class_name**, entrez `"M321"` ou `"CG"`.
  - Exemple de corps de requête :
    ```json
    {
      "title": "Projet Pratique",
      "date": "2024-12-30T11:40:00",
      "priority": "P1"
    }
    ```
  - Cliquez sur **Execute** pour créer l'événement.
  - **Exemple de réponse** :
    ```json
    {
      "message": "Événement partagé créé pour la classe M321"
    }
    ```

- **Voir les événements de classe** : `/classe/{class_name}/events` [GET]
  - Accédez à l'endpoint `/classe/{class_name}/events`.
  - Cliquez sur **Try out**.
  - Dans **class_name**, entrez `"M321"` ou `"CG"`.
  - Cliquez sur **Execute** pour voir tous les événements de la classe.
  - **Exemple de réponse** :
    ```json
    [
      {
        "title": "Devoir CG",
        "date": "2024-12-20T14:30:00",
        "priority": "P2"
      }
    ]
    ```

- **Mettre à jour un événement de classe** : `/classe/{class_name}/events/by_title/{event_title}` [PUT]
  - Accédez à l’endpoint `/classe/{class_name}/events/by_title/{event_title}`.
  - Cliquez sur **Try out**.
  - Dans **class_name**, entrez `"M321"` ou `"CG"`.
  - Dans **event_title**, entrez le titre exact de l’événement à mettre à jour.
  - Exemple de corps de requête :
    ```json
    {
      "title": "Examen M321 - Partie 2",
      "date": "2024-12-22T10:00:00",
      "priority": "P1"
    }
    ```
  - Cliquez sur **Execute** pour mettre à jour l'événement.
  - **Exemple de réponse** :
    ```json
    {
      "message": "Événement partagé modifié pour la classe M321",
      "event": {
        "title": "Examen M321 - Partie 2",
        "date": "2024-12-22T10:00:00",
        "priority": "P1"
      }
    }
    ```

- **Supprimer un événement de classe** : `/classe/{class_name}/events/by_title/{event_title}` [DELETE]
  - Accédez à l'endpoint `/classe/{class_name}/events/by_title/{event_title}`.
  - Cliquez sur **Try out**.
  - Dans **class_name**, entrez `"M321"` ou `"CG"`.
  - Dans **event_title**, entrez le titre exact de l'événement à supprimer.
  - Cliquez sur **Execute** pour supprimer l'événement.
  - **Exemple de réponse** :
    ```json
    {
      "message": "Événement supprimé de la classe M321",
      "deleted_event": {
        "title": "Examen 321 - Partie 2",
        "date": "2024-12-22T10:00:00",
        "priority": "P1"
      }
    }
    ```

---

### Pour les élèves :

- **Voir son agenda personnel** : `/users/me/agenda` [GET]
  - Accédez à l'endpoint `/users/me/agenda`.
  - Cliquez sur **Try out** et sur **Execute** pour voir tous les événements de l'élève.
  - **Exemple de réponse** :
    ```json
    [
      {
        "title": "Examen CG",
        "date": "2024-12-20T14:30:00",
        "priority": "P1"
      }
    ]
    ```

- **Filtrer les événements dans son agenda** : `/users/me/agenda/filter` [GET]
  - Accédez à l'endpoint `/users/me/agenda/filter`.
  - Cliquez sur **Try out**.
  - Entrez les paramètres de filtrage optionnels :
    - `date` : entrez une date au format `"DD/MM/YYYY"` pour filtrer par date.
    - `priority` : entrez `P1`, `P2` ou `P3` pour filtrer par priorité.
  - Cliquez sur **Execute** pour obtenir les résultats filtrés.
  - **Exemple de réponse** :
    ```json
    [
      {
        "title": "Devoir CG",
        "date": "2024-12-15T08:00:00",
        "priority": "P2"
      }
    ]

### 4. Notifications
Les notifications apparaîtront dans le Terminal 3 où vous avez lancé subscriber.py.

Vous verrez :
- Les nouveaux événements créés
- Les mises à jour d'événements
- Les notifications basées sur les priorités

### Exemple de notification 

```bash
Connexion réussie à RabbitMQ !
 [*] En attente des notifications pour les événements partagés, privés et les mises à jour. Appuyez sur CTRL+C pour quitter.
[x] Notification privée reçue : Événement privé : Test, Date : 2024-10-29 19:59:58.724000+00:00, Priorité : PriorityLevel.P2
[x] Notification reçue : Rappel: Test - échéance: 29/10/2024
```

### Exemple de notification evenement partagé

```bash
Connexion réussie à RabbitMQ !
 [*] En attente des notifications pour les événements partagés, privés et les mises à jour. Appuyez sur CTRL+C pour quitter.
[x] Notification reçue : Jeremy Maceiras a ajouté une affectation | Échéance: 29/10/2024 | Classe: M321
[x] Notification reçue : [Classe M321] URGENT! Projet Pratique - échéance: 29/10/2024
```

## Monitoring

### Grafana
1. Accédez à http://localhost:3000
2. Connectez-vous (admin/admin)
3. Visualisez les métriques :
   - Nombre de requêtes API
   - Événements créés
   - Notifications envoyées
   - Si Promotheus est UP ou DOWN

### RabbitMQ
1. Accédez à http://localhost:15672
2. Connectez-vous (guest/guest)
3. Observez :
   - L'état des queues de messages
   - Les notifications en cours
   - Les statistiques d'envoi

### Métriques disponibles
- agenda_api_requests : Nombre de requêtes par endpoint
- agenda_events_total : Nombre d'événements par type
- agenda_notifications_sent : Nombre de notifications par priorité