import pika

# Connexion à RabbitMQ
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    print("Connexion réussie à RabbitMQ !")
except Exception as e:
    print(f"Erreur de connexion à RabbitMQ : {e}")

# Fonction appelée lorsqu'un message est reçu pour les événements partagés
def class_event_callback(ch, method, properties, body):
    print(f"[CLASSE] Notification reçue : {body.decode()}")

# Fonction appelée lorsqu'un message est reçu pour les événements privés
def private_event_callback(ch, method, properties, body):
    print(f"[PRIVE] Notification reçue : {body.decode()}")

# Fonction appelée lorsqu'un message est reçu pour la mise à jour d'un événement privé
def private_event_update_callback(ch, method, properties, body):
    print(f"[UPDATE] Mise à jour d'événement reçue : {body.decode()}")

# Fonction pour les notifications basées sur la priorité
def priority_notification_callback(ch, method, properties, body):
    print(f"[ALERT] Notification prioritaire reçue : {body.decode()}")

# Abonnement à la queue des événements privés
channel.queue_declare(queue='private_events')
channel.basic_consume(queue='private_events', on_message_callback=private_event_callback, auto_ack=True)

# Abonnement à la queue des mises à jour d'événements privés
channel.queue_declare(queue='private_event_updates')
channel.basic_consume(queue='private_event_updates', on_message_callback=private_event_update_callback, auto_ack=True)

# Abonnement à la queue des notifications (pour les priorités)
channel.queue_declare(queue='notifications')
channel.basic_consume(queue='notifications', on_message_callback=priority_notification_callback, auto_ack=True)

# Abonnement à la queue des événements partagés d'une ou plusieurs classes
classes_to_subscribe = ['M321', 'CG']  
for class_name in classes_to_subscribe:
    queue_name = f'class_events_{class_name}'
    channel.queue_declare(queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=class_event_callback, auto_ack=True)

print(' [*] En attente des notifications pour les événements partagés, privés, les mises à jour et les notifications prioritaires. Appuyez sur CTRL+C pour quitter.')

# Démarrer la consommation des messages
channel.start_consuming()