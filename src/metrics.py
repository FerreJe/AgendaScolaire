from prometheus_client import start_http_server, Counter

start_http_server(8002)

# Compteur pour suivre le nombre de requêtes à l'API
api_requests = Counter(
    'agenda_api_requests', 
    'Nombre total de requêtes API',
    ['endpoint']  # Pour distinguer les différents endpoints appelés
)

# Compteur pour suivre les notifications envoyées
notifications_sent = Counter(
    'agenda_notifications_sent', 
    'Nombre de notifications envoyées',
    ['priority']  # P1 (examens), P2 (devoirs), P3 (infos)
)

# Compteur pour suivre le nombre d'événements créés
events_total = Counter(
    'agenda_events_total', 
    'Nombre total d\'événements',
    ['type']  # private ou shared 
)