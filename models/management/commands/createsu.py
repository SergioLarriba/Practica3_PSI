from models.models import Player 
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a superuser.'

    def handle(self, *args, **options):
        if not Player.objects.filter(username='alumnodb').exists():
            Player.objects.create_superuser(
                username='alumnodb',
                password='alumnodb'
            )
        print('Superuser has been created.')