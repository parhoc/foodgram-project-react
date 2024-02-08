# Foodgram

## О проекте
«Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
## Доступ к сайту
Сайт: https://foodgram.viewdns.net

Email: foodgram@foodgram.com

Пароль: foodgram5533
## Установка
### Через Docker hub
Скачать файл ``docker-compose.production.yml``

В директории с файлом запустить:
```
docker compose -f docker-compose.production.yml up
```
В другом терминале ввести команды:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
Сайт будет доступен по адресу `127.0.0.1:8000`.
### Локальная установка
Клонировать рапозиторий:
```
git clone https://github.com/parhoc/foodgram-project-react.git
```
В папке с проектом запустить Docker compose:
```
docker compose up
```
В другом терминале ввести команды:
```
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```
Сайт будет доступен по адресу `127.0.0.1:8000`.
## Возможности проекта
### Рецепты
![alt text](https://pictures.s3.yandex.net/resources/S16_01_1692340098.png)
На главной странице сайта показываются все рецепты в порядке создания. На странице рецепта можно посмотреть более детальную информацию, а авторизированные пользователи могут добавить рецепт в избранное или список покупок. Рецепты можно фильтровать по тегам и авторам.
### Добавление рецепта
![alt text](https://pictures.s3.yandex.net/resources/S16_09_1_1692340285.png)
Пользователи могут добавлять собственные рецепты. Для этого пользователю необходимо указать названи рецепта, выбрать подходещие теги, нужные ингредиетны, указать время готовки, добавить описание и картинку рецепта.
### Список покупок и избранное
![alt text](https://pictures.s3.yandex.net/resources/S16_07_1692340247.png)
Каждый рецепт можно добавить в список покупок или избранное. Список покупок можно скачать в виде PDF файла с необходимыми для рецептов ингредиентами их количеством.
## Технические характеристики
* Фронтенд - NodeJS 13.12;
* Бекенд - Python 3.10, Django 3.2 и Djangorestframework 3.14;
* База данных - PostgreSQL 13.
