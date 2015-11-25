# coding=utf-8
import csv
import fileinput
import random

from django.core.management.base import BaseCommand
from django.utils.lorem_ipsum import words

from spec_ibride.gallery.models import Photo


class Command(BaseCommand):
    """Вставляет в базу данных исходные значения.

    Тегов ~10^2 штук, в среднем у фотки 5 тегов.

    """
    help = 'Populate database.'

    # Максимальное значение рейтинга
    max_rating = 100500

    # Количество тегов для вставки.
    number_of_tags = 100

    # Среднее количество тегов для фотографии
    average_tags_per_photo = 5

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
        self.stdout.write('Import photos from "%s"' % data_filename)
        try:
            self._import_data(fileinput.input(data_filename))
        finally:
            fileinput.close()
        self.stdout.write('Generate tags')
        self._generate_tags()
        self.stdout.write('Done')

    def _import_data(self, csv_file):
        """Загрузить в базу данные о фоторафиях.

        :type csv_file: io.IOBase
        :param csv_file: файл CSV с исходными данными о фотографиях

        """

        csv_reader = csv.DictReader(csv_file, delimiter=';')
        Photo.objects.bulk_create((
            Photo(
                src=row['src'],
                user_id=row['user_id'],
                created_at=row['created_at'],
                rating=random.randrange(0, self.max_rating)
            ) for row in csv_reader),
            batch_size=99
        )

    def _generate_tags(self):
        """Сгенерировать теги для нескольких случайных фотографий."""
        tag_words = words(self.number_of_tags).split()
        for photo in Photo.objects.order_by('?')[:1000]:
            sample_length = random.randrange(
                0, self.average_tags_per_photo * 2)
            if sample_length:
                selected_tags = random.sample(tag_words, sample_length)
                photo.update_tags(selected_tags)
