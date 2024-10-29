# src/notification_manager.py
from datetime import datetime, timezone
from src.models import Event, PriorityLevel
import pika

class NotificationManager:
    def __init__(self):
        # Connexion à RabbitMQ
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='notifications')
        except:
            print("RabbitMQ n'est pas disponible. Démarrez d'abord docker-compose up")
            self.connection = None
            self.channel = None

    # Le reste du code reste exactement le même
    def check_notification_timing(self, event: Event) -> bool:
        """Vérifie quand envoyer la notification selon la priorité"""
        days_until_event = (event.date.replace(tzinfo=None) - datetime.now()).days
        # Règles simples de notification
        if event.priority == PriorityLevel.P1:    # Examens
            return days_until_event <= 2          # 2 jours avant
        elif event.priority == PriorityLevel.P2:  # Devoirs
            return days_until_event <= 1          # 1 jour avant
        else:                                     # Infos
            return days_until_event == 0          # Le jour même

    def send_notification(self, event: Event, class_name: str = None):
        """Envoie une notification pour un événement"""
        if not self.channel:  # Vérifie si RabbitMQ est disponible
            return
            
        if not self.check_notification_timing(event):
            return
        # Crée le message selon la priorité
        if event.priority == PriorityLevel.P1:
            prefix = "URGENT!"
        elif event.priority == PriorityLevel.P2:
            prefix = "Rappel:"
        else:
            prefix = "Info:"
        # Format du message
        message = f"{prefix} {event.title} - échéance: {event.date.strftime('%d/%m/%Y')}"
        if class_name:
            message = f"[Classe {class_name}] {message}"
        try:
            # Envoie le message
            self.channel.basic_publish(
                exchange='',
                routing_key='notifications',
                body=message
            )
            print(f"Notification envoyée: {message}")
        except Exception as e:
            print(f"Erreur d'envoi: {e}")

    def close(self):
        """Ferme la connexion RabbitMQ"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()