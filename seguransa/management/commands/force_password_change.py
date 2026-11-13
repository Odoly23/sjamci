from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from seguransa.utils import require_password_change


class Command(BaseCommand):
    help = "Obriga utilizador sira troka password iha login tuir mai (ezemplu hafoin password default sai públiku)."

    def add_arguments(self, parser):
        parser.add_argument('usernames', nargs='*', help='Username sira; se mamuk uza --all')
        parser.add_argument('--all', action='store_true', help='Aplika ba utilizador ativu hotu')

    def handle(self, *args, **options):
        users = get_user_model().objects.filter(is_active=True)
        if not options['all']:
            if not options['usernames']:
                self.stderr.write('Fó username ka uza --all.')
                return
            users = users.filter(username__in=options['usernames'])
        count = 0
        for user in users:
            require_password_change(user)
            count += 1
        self.stdout.write(self.style.SUCCESS(f'{count} konta tenke troka password iha login tuir mai.'))
