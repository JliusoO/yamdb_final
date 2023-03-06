import csv
from django.conf import settings
from django.core.management import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title, User


ModToCSV = {
    User: "users.csv",
    Category: "category.csv",
    Genre: "genre.csv",
    Title: "titles.csv",
    Review: "review.csv",
    Comment: "comments.csv",
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        for model, csv_file in ModToCSV.items():
            with open(
                f"{settings.BASE_DIR}/static/data/{csv_file}",
                "r", encoding="utf-8"
            ) as f:
                dict_reader = csv.DictReader(f)
                model.objects.bulk_create(
                    model(**data) for data in dict_reader
                )

        self.stdout.write(self.style.SUCCESS("Данные успешно загружены"))
