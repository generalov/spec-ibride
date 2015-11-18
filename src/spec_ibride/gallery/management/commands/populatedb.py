import csv
import random
from django.core.management.base import BaseCommand, CommandError
from spec_ibride.gallery.models import Photo
from django.utils.lorem_ipsum import words
from tagging.models import Tag


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
            self.stdout.write('Import photos from "%s"' % data_filename)
            Photo.objects.bulk_create((
                Photo(
                    src=row['src'],
                    user_id=row['user_id'],
                    created_at=row['created_at'],
                    rating=random.randrange(0, 100500)
                ) for row in csvreader),
                batch_size=99
            )
            self.stdout.write('Generate tags')
            tag_words = words(100).split()
            for photo in Photo.objects.order_by('?')[:100]:
                sample_length = random.randrange(0, 6)
                if sample_length:
                    selected_tags = random.sample(tag_words, sample_length)
                    Tag.objects.update_tags(photo, u' '.join(selected_tags))

            self.stdout.write('Done')
