# api_yamdb

![example workflow](https://github.com/JliusoO/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)yamdb_final

### Описание проекта

Проект YaMDb собирает отзывы пользователей на произведения. 
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка».
## Примеры:
*Все примеры обращения описаны на http://158.160.39.55/redoc/*

## Для запуска проекта
### Клонируем репозиторий, переходим в него
### Создаём шаблон наполнения env-файла в /infra
```bash
nano infra/.env
```
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
### Поднимаем контейнер
```bash
sudo docker-compose up -d --build 
```
### Создаём связи миграции
```bash
docker-compose exec web python manage.py makemigrations users
```
```bash
docker-compose exec web python manage.py makemigrations reviews
```
### Выполняем миграции
```bash
docker-compose exec web python manage.py migrate
```
### Создаем суперпользователя
```bash
winpty docker-compose exec web python manage.py createsuperuser
```
### Собираем статику
```bash
docker-compose exec web python manage.py collectstatic --no-input 
```
### Создаем копию базы данных
```bash
docker-compose exec web python manage.py dumpdata > fixtures.json 
```
