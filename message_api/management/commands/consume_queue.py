from django.core.management.base import BaseCommand
from message_api.consumer import ContestConsumer

class Command(BaseCommand):
    help = 'Start RabbitMQ consumer for contest submissions'

    def handle(self, *args, **kwargs):
        consumer = ContestConsumer()
        consumer.start()
