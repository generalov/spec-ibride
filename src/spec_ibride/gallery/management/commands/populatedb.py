import csv
import random
from django.core.management.base import BaseCommand, CommandError
from spec_ibride.gallery.models import Photo


class Command(BaseCommand):
    help = 'Populate database.'

    def add_arguments(self, parser):
        """
        :param parser: optparse.OptionParser
        """
        parser.add_argument('-d', '--data',
                            action='store',
                            dest='data',
                            help='Path to CSV data file')

    def handle(self, *args, **options):
        data_filename = options['data']
        with open(data_filename, 'rb') as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=";")
            Photo.objects.bulk_create((
                Photo(
                    src=row['src'],
                    user_id=row['user_id'],
                    created_at=row['created_at'],
                    rating=random.randrange(0, 100500)
                ) for row in csvreader),
                batch_size=99
            )

            self.stdout.write('Successfully imported "%s"' % data_filename)
