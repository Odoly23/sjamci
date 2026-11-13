import gzip
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Halo backup baze-dadus ba ficheiru JSON kompresadu (restaura ho: manage.py loaddata)."

    def add_arguments(self, parser):
        parser.add_argument('--dir', default=str(Path(settings.BASE_DIR) / 'backups'), help='Pasta destinu')
        parser.add_argument('--keep', type=int, default=30, help='Númeru backup ne\'ebé rai (default 30)')

    def handle(self, *args, **options):
        target = Path(options['dir'])
        target.mkdir(parents=True, exist_ok=True)
        target.chmod(0o700)
        path = target / f"sjamci_{datetime.now():%Y%m%d_%H%M%S}.json.gz"
        with gzip.open(path, 'wt', encoding='utf-8') as handle:
            call_command('dumpdata', '--natural-foreign', '--natural-primary',
                         '--exclude', 'contenttypes', '--exclude', 'auth.permission',
                         '--exclude', 'sessions', '--exclude', 'admin.logentry',
                         '--exclude', 'axes', stdout=handle)
        path.chmod(0o600)
        backups = sorted(target.glob('sjamci_*.json.gz'))
        for old in backups[:-options['keep']] if options['keep'] > 0 else []:
            old.unlink()
        size = path.stat().st_size / 1024
        self.stdout.write(self.style.SUCCESS(f'Backup rai iha {path} ({size:.0f} KB)'))
