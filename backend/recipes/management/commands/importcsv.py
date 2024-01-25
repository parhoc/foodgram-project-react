import csv
from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Imports data from csv file to Ingredient table'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('file', nargs=1, type=str)

    def handle(self, *args: Any, **options: Any) -> str | None:
        with open(options['file'][0], 'r') as file:
            reader = csv.reader(file)
            Ingredient.objects.bulk_create(
                Ingredient(name=row[0], measurement_unit=row[1])
                for row in reader
            )
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully imported {reader.line_num} rows'
            )
        )