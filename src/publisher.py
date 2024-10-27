import pika
from src.models import Event


# Fonction pour établir une connexion à RabbitMQ
def get_rabbitmq_connection():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        return connection, channel
    except pika.exceptions.AMQPConnectionError:
        print("Erreur de connexion à RabbitMQ")
        return None, None


# Publier un événement privé (création)
def publish_private_event(event: Event):
    connection, channel = get_rabbitmq_connection()
    if connection is None or channel is None:
        print("Impossible d'envoyer l'événement privé, connexion échouée.")
        return

    # Déclarer la queue pour les événements privés
    channel.queue_declare(queue='private_events')

    # Publier l'événement
    message = f"Événement privé : {event.title}, Date : {event.date}, Priorité : {event.priority}"
    channel.basic_publish(exchange='', routing_key='private_events', body=message)

    # Fermer la connexion
    connection.close()


# Publier la mise à jour d'un événement privé
def publish_private_event_update(event: Event):
    connection, channel = get_rabbitmq_connection()
    if connection is None or channel is None:
        print("Impossible d'envoyer la mise à jour de l'événement privé, connexion échouée.")
        return

    # Déclarer la queue pour les événements privés mis à jour
    channel.queue_declare(queue='private_event_updates')

    # Publier la mise à jour
    message = f"Mise à jour événement privé : {event.title}, Nouvelle date : {event.date}, Priorité : {event.priority}"
    channel.basic_publish(exchange='', routing_key='private_event_updates', body=message)

    # Fermer la connexion
    connection.close()


# Publier un événement partagé (création ou mise à jour)
def publish_class_event(message: str, class_name: str):
    connection, channel = get_rabbitmq_connection()
    if connection is None or channel is None:
        print(f"Impossible d'envoyer l'événement partagé pour la classe {class_name}, connexion échouée.")
        return

    # Déclarer la queue pour les événements de classe
    channel.queue_declare(queue=f'class_events_{class_name}')

    # Publier l'événement
    channel.basic_publish(exchange='', routing_key=f'class_events_{class_name}', body=message)

    # Fermer la connexion
    connection.close()
